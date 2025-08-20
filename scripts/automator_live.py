import json
import os
import time
from pathlib import Path
from urllib.parse import urlparse

import requests
from IPython import embed
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from scripts import login
from scripts.const import WAIT, XPATH
from scripts.utils import (
    find_by_xpath_and_click,
    scroll_into_view_and_click,
    wait_and_click,
    wait_and_type,
    wait_for_element_to_disappear,
)

IMAGES_FOLDER = "staff_images"
BASE_URL = "BASE"

# Data processing
def get_unique_departments(staff_data):
    return list(dict.fromkeys(member["department"] for member in staff_data))

def submit_departments(departments, driver):
    wait = WebDriverWait(driver, WAIT.SHORT)

    print("Submitting departments: ")
    for department in departments:
        try:
            print(f" * {department}")
            wait_and_click(wait, XPATH.department_add_btn) 
            wait_and_type(wait, XPATH.department_name, department) 
            wait_and_click(wait, XPATH.submit_department_btn) 

        except Exception as e:
            print(f"Failed to submit department '{department}':", e)

def get_image_file_name(staff_name, image_url):
    parsed_url = urlparse(image_url)
    file_extension = os.path.splitext(parsed_url.path)[1] or ".jpg"

    # Create file path
    name = staff_name.replace(" ", "")
    filename = f"{name}{file_extension}"
    return filename

def download_staff_images(staff_data):
    Path(IMAGES_FOLDER).mkdir(parents=True, exist_ok=True)

    for member in staff_data:
        image_url = member.get("image_url", "").strip()

        if not image_url or image_url == 'N/A':
            print(f"⚠️ Skipping entry with missing name or image_url: {member}")
            continue

        # If the URL is relative, prepend the base domain
        if image_url.startswith("/"):
            image_url = BASE_URL.rstrip("/") + image_url

        filename = get_image_file_name(member.get("name"), image_url)

        file_path = Path(IMAGES_FOLDER) / filename
        try:
            # Download image
            response = requests.get(image_url, stream=True, timeout=10)
            response.raise_for_status()

            # Save to file
            with open(file_path, "wb") as img_file:
                for chunk in response.iter_content(1024):
                    img_file.write(chunk)

            print(f"✅ Downloaded {filename}")

        except requests.RequestException as e:
            print(f"❌ Failed to download {image_url}: {e}")

# <div class="successful-upload">1 file(s) successfully uploaded.</div>
# //*[@id="modal-body"]/div[2]/span/div/div

def upload_staff_images_in_batches(driver):
    batch_size=20
    # Get all image paths
    image_paths = list(Path(IMAGES_FOLDER).glob("*.*"))  # all files in folder
    wait = WebDriverWait(driver, WAIT.SHORT)
    wait_upload = WebDriverWait(driver, WAIT.UPLOAD)

    if not image_paths:
        print("⚠️ No images found to upload.")
        return

    total = len(image_paths)
    print(f"📦 Found {total} images. Uploading in batches of {batch_size}...")

    # Split into batches
    for i in range(0, total, batch_size):
        # click on upload
        wait_and_click(wait, '//*[@id="media-library-ui-root"]/div/div/div[2]/div[1]/div[3]/nsemble-button[3]')

        batch = image_paths[i:i + batch_size]
        # Find the file input each time (some pages reset it after upload)
        file_input = driver.find_element(By.ID, "files")

        print(f"💬  Uploading batch {i//batch_size + 1} ({len(batch)} files)...")
        # Send this batch of absolute paths separated by newline
        files_to_upload = "\n".join(str(img.resolve()) for img in batch)
        file_input.send_keys(files_to_upload)

        # upload image click
        # TODO: scroll into view  
        find_by_xpath_and_click(driver, wait,'//*[@id="modal-footer"]/div/div/div/div/nsemble-button')

        # wait until upload image btn dissapears (spinner)
        wait_for_element_to_disappear(wait_upload, '//*[@id="modal-footer"]/div/div/div/div/nsemble-button')

        # close
        wait_and_click(wait, '//*[@id="modal-footer"]/div/div/nsemble-button')

        print("   Upload completed")
        # Optional: wait between batches so site can process uploads
        # time.sleep(20)

    print("✅ All images uploaded")

def find_span_in_shadow(wait, root, text):
    def _search(_driver):
        spans = root.find_elements(By.CSS_SELECTOR, "span.label")
        return next((s for s in spans if s.text.strip().lower() == text.strip().lower()), None)
    try:
        return wait.until(_search)
    except Exception:
        return None
    
def expand_media_lib_folder(driver, wait, folder):
    expand_btn_xpath = "./preceding-sibling::span[contains(@class, 'disclosure')]"
    expand_btn = folder.find_element(By.XPATH, expand_btn_xpath)

    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", expand_btn)
    wait.until(EC.element_to_be_clickable(expand_btn))
    expand_btn.click()


def _shadow_find(root, wait, css_selector):
    def _find(_):
        return root.find_element(By.CSS_SELECTOR, css_selector)
    try: 
        return wait.until(_find)
    except TimeoutException:
        print(f"Element with selector '{css_selector}' was not found in the shadow root.")
        raise

def shadow_type(root, wait, css_selector, text):
    element = _shadow_find(root, wait, css_selector)
    wait.until(EC.element_to_be_clickable(element))
    element.clear()
    element.send_keys(text)

def shadow_click(root, wait, css_selector):
    element = _shadow_find(root, wait, css_selector)
    wait.until(EC.element_to_be_clickable(element))
    element.click()

def get_shadow_root(wait, container_xpath, shadow_element_css):
    container = wait.until(EC.presence_of_element_located((By.XPATH, container_xpath)))
    host = container.find_element(By.CSS_SELECTOR, shadow_element_css)
    root = host.shadow_root
    return root

def has_class(element, class_name):
    return class_name in element.get_attribute('class').split()

def select_or_create_media_lib_folder(driver, wait, media_lib_url):
    driver.get(media_lib_url)

    wait_shorter = WebDriverWait(driver, 2)
    root = get_shadow_root(wait, '//*[@id="library-sidebar"]', 'nsemble-tree')
    parent_folder_label = find_span_in_shadow(wait_shorter, root, parent_folder_name)

    parent_folder_name = 'Do Not Delete23' 

    if not parent_folder_label:
        print('LOG: Folder Not found')

        wait_and_click(wait, '//*[@id="library-sidebar"]/div/div[2]/div/div[1]/nsemble-button') 
        modal_root = get_shadow_root(wait, '//*[@id="modal-window"]', '#modal-body > div > div > nsemble-input')

        # type on input the parent folder name
        shadow_type(modal_root, wait, '#label', parent_folder_name)
        # click on button
        wait_and_click(wait, '//*[@id="modal-footer"]/div/div/div/nsemble-button')

        wait_for_element_to_disappear(wait, '//*[@id="modal-window"]')     

        parent_folder_label = find_span_in_shadow(wait_shorter, root, parent_folder_name)

    print('Folder Found')
    expand_media_lib_folder(driver, wait, parent_folder_label)

    folder_name = 'Staff' 
    parent_container = parent_folder_label.find_element(By.XPATH, "./..")
    # get the first sibling of that container
    children_container = parent_container.find_element(By.XPATH, "following-sibling::*[1]")

    staff_folder = find_span_in_shadow(wait_shorter, children_container, folder_name)

    if not staff_folder:
        print('LOG: Staff Folder Not found')
        parent_folder_label.click()

        # click on create
        parent = parent_folder_label.find_element(By.XPATH, "./..")
        btn_container = _shadow_find(parent, wait, ".icons")
        shadow_click(btn_container, wait, "[data-action='icon-1']:nth-child(2)")

        modal_root = get_shadow_root(wait, '//*[@id="modal-window"]', '#modal-body > div > div > nsemble-input')

        shadow_type(modal_root, wait, '#label', folder_name)
        wait_and_click(wait, '//*[@id="modal-footer"]/div/div/div/nsemble-button')
        wait_for_element_to_disappear(wait, '//*[@id="modal-window"]')     

        if not has_class(children_container, 'open'):
            expand_media_lib_folder(driver, wait, parent_folder_label)
        staff_folder = find_span_in_shadow(wait_shorter, children_container, folder_name)

    print('clicking!')
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", staff_folder)
    wait.until(EC.element_to_be_clickable(staff_folder)).click()

def create_folder(wait, folder_name):
    modal_root = get_shadow_root(wait, '//*[@id="modal-window"]', '#modal-body > div > div > nsemble-input')

    shadow_type(modal_root, wait, '#label', folder_name)
    wait_and_click(wait, '//*[@id="modal-footer"]/div/div/div/nsemble-button')

    wait_for_element_to_disappear(wait, '//*[@id="modal-window"]')

def find_or_create_folder(driver, wait, root, folder_name):
    wait_short = WebDriverWait(driver, 2)
    folder_label = find_span_in_shadow(wait_short, root, folder_name)
    if folder_label:
        return folder_label

    print(f'LOG: Folder "{folder_name}" not found, creating...')

    wait_and_click(wait, '//*[@id="library-sidebar"]/div/div[2]/div/div[1]/nsemble-button')
    create_folder(wait, folder_name)

    folder_label = find_span_in_shadow(wait_short, root, folder_name)

    return folder_label

def find_or_create_sub_folder(driver, wait, root, parent_folder_label, folder_name):
    wait_short = WebDriverWait(driver, 2)
    parent_container = parent_folder_label.find_element(By.XPATH, "./..")
    children_container = parent_container.find_element(By.XPATH, "following-sibling::*[1]")

    sub_folder = find_span_in_shadow(wait_short, children_container, folder_name)
    if sub_folder:
        return sub_folder

    parent_folder_label.click()
    btn_container = _shadow_find(parent_container, wait, ".icons")
    shadow_click(btn_container, wait, "[data-action='icon-1']:nth-child(2)")
    create_folder(wait, folder_name)

    sub_folder = find_span_in_shadow(wait_short, root, folder_name)

    return sub_folder



# --- Main function ---

def select_or_create_media_lib_folder2(driver, wait, media_lib_url):
    parent_folder_name = 'Do Not Delete24'
    folder_name = 'Staff'

    driver.get(media_lib_url)

    # Get shadow root for library tree
    sidebar_root = get_shadow_root(wait, '//*[@id="library-sidebar"]', 'nsemble-tree')

    # Parent Folder
    parent_folder_label = find_or_create_folder(driver, wait, sidebar_root, parent_folder_name)
    expand_media_lib_folder(driver, wait, parent_folder_label)

    # --- Child folder ---
    staff_folder = find_or_create_sub_folder(driver, wait, sidebar_root, parent_folder_label, folder_name)

    # Expand if necessary
    parent_container = parent_folder_label.find_element(By.XPATH, "./..")
    children_container = parent_container.find_element(By.XPATH, "following-sibling::*[1]")
    if not has_class(children_container, 'open'):
        expand_media_lib_folder(driver, wait, parent_folder_label)

    # Click the staff folder
    scroll_into_view_and_click(driver, wait, staff_folder)

    print(f'LOG: Folder "{folder_name}" clicked successfully!')


def select_media_lib_staff_folder(driver, wait):
    wait_and_click(wait, XPATH.staff_add_btn)

    # image selector 
    wait_and_click(wait, '//*[@id="cmsc-scroll-container"]/div/form/div[1]/div[1]/button')

    # switch to iframe 
    iframe = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="library-panel"]')))
    driver.switch_to.frame(iframe)

    # clicking on shadow root
    sidebar = wait.until(EC.presence_of_element_located((By.ID, "library-sidebar")))
    host = sidebar.find_element(By.CSS_SELECTOR, "nsemble-tree")
    root = host.shadow_root  # Selenium 4+

    # 4) Click parent folder
    parent_folder_label = find_span_in_shadow(wait, root, 'Do Not Delete')
    expand_parent_folder = parent_folder_label.find_element(By.XPATH, "./preceding-sibling::span[contains(@class, 'disclosure')]")

    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", expand_parent_folder)
    wait.until(EC.element_to_be_clickable(expand_parent_folder))
    expand_parent_folder.click()

    # 5) Click staff folder
    staff_folder_label = find_span_in_shadow(wait, root, 'Staff')
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", staff_folder_label)
    wait.until(EC.element_to_be_clickable(staff_folder_label)).click()

    driver.switch_to.default_content()
    # close window modal
    wait_and_click(wait,'//a[contains(@class, "ui-dialog-titlebar-close") and @role="button"]//span[contains(@class, "ui-icon-closethick")]')
    # cancel button
    wait_and_click(wait,'//*[@id="cmsc-staff-editor-ct"]/div/div[3]/button[3]')

def select_img(driver, wait, file_name):
    wait_and_click(wait, '//*[@id="cmsc-scroll-container"]/div/form/div[1]/div[1]/button')

    iframe = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="library-panel"]')))
    driver.switch_to.frame(iframe)

    # pick image
    grid_view = wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "#media-library-ui-root .grid-view")
        )
    )

    # --- Step 4: Find the file span inside .grid-view
    file_element = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, f".//span[@class='file-name' and text()='{file_name}']")
        )
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", file_element)
    wait.until(EC.element_to_be_clickable((By.XPATH, f".//span[@class='file-name' and text()='{file_name}']")))

    # TODO: search in next pages if necessary
    # --- Step 5: Double-click on the file element
    actions = ActionChains(driver)
    actions.double_click(file_element).perform()

    driver.switch_to.default_content()
    print("Image selected succesfully")

def submit_staff_safe(staff_list, driver):
    wait = WebDriverWait(driver, WAIT.SHORT)

    def safe_send(xpath, key, default=""):
        try:
            value = staff.get(key, default)
            if value and value.strip().upper() != "N/A":
                wait_and_type(wait, xpath, value)

        except Exception as e:
            print(f"Could not fill {key}: {e}")

    # select staff image folder
    select_media_lib_staff_folder(driver, wait)

    # 
    for staff in staff_list:
        try:
            print(f"Submitting staff member: {staff.get('name', '[Unknown Name]')}")

            # Click "Add Staff" button
            wait_and_click(wait, XPATH.staff_add_btn)

            # Fill form fields (only if value is valid)
            safe_send('//*[@id="staffName"]', "name")
            safe_send('//*[@id="staffTitle"]', "position")
            safe_send('//*[@id="staffPhone"]', "phone")
            safe_send('//*[@id="staffEmail"]', "email")
            safe_send('//*[@id="staffBio"]', "biography")

            # select image
            if staff.get("image_url") != "N/A":
                select_img(driver, wait, get_image_file_name(staff.get("name"),staff.get("image_url")))

            # wait_and_click(WebDriverWait(driver, WAIT.SHORT),"//*[@id='library-sidebar']//span[normalize-space()='DO NOT DELETE']")
            # 
            # 
            # Select Department
            dept_name = staff.get("department", "").strip()
            if dept_name and dept_name.upper() != "N/A":
                dropdown_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="staffDepartment"]')))
                dropdown_btn.click()

                time.sleep(0.5)
                menu_items = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//ul[@role="listbox"]/li')))
                matched = False
                for item in menu_items:
                    if dept_name.lower() in item.text.strip().lower():
                        item.click()
                        matched = True
                        break

                if not matched:
                    print(f"Warning: Department '{dept_name}' not found for {staff.get('name')}")
                    continue

            # Wait for any loading indicator to disappear (if applicable)
            # wait.until(EC.invisibility_of_element_located(...))  # Optional

            # Submit the form
            wait_and_click(wait, XPATH.submit_staff_btn)

            # time.sleep(1.5) 

        except Exception as e:
            print(f"Failed to submit staff member '{staff.get('name', '[Unknown Name]')}': {e}")

def start_browser_driver():
    # FOLDER_PROFILE_URL = r"D:\mojix\repo\hackaton-coderoad\scripts\selenium-profile"

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--log-level=3")
    options.add_experimental_option("detach", True)

    # Supress chrome log messages
    service = Service(ChromeDriverManager().install(), log_path=os.devnull)
    # options.add_argument("user-data-dir="+FOLDER_PROFILE_URL)
    # options.add_argument("--remote-debugging-port=9222")

    driver = webdriver.Chrome(service=service, options=options)
    return driver


def automation_script(dealer_id):        
    with open(r"output_staff.json", "r", encoding="utf-8") as file:
        staff_data = json.load(file)


    STAFF_URL = f"https://apps.dealercenter.coxautoinc.com/website/as/{dealer_id}/{dealer_id}-admin/quickLink?lang=en_US&deeplink=%2Fdealership%2Fstaff.htm"
    MEDIA_LIB_URL = f"https://apps.dealercenter.coxautoinc.com/promotions/as/{dealer_id}/{dealer_id}-admin/medialibrary3/index?lang=en_US"
    # download_staff_images(staff_data)


    # departments = get_unique_departments(staff_data)
    driver = start_browser_driver()

    # # Login
    # ddc login 
    login.staff_tool_login(driver, STAFF_URL)
    # download_staff_images(staff_data)     

    # download images

    # upload images

    # coonnect to staff tool
    # staff_connect.connect_to_staff_tool(driver)

    # submit_departments(departments, driver)
    # submit_staff_safe(staff_data, driver)

    embed()
    # Uncomment to test code live
