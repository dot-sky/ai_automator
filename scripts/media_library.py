from pathlib import Path

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from scripts.const import WAIT, XPATH
from scripts.shadow_helpers import (
    _shadow_find,
    find_span_in_shadow,
    get_shadow_root,
    shadow_click,
    shadow_type,
)
from scripts.utils import (
    click_element_by_xpath,
    has_class,
    scroll_and_click_element,
    scroll_element_into_view,
    switch_to_iframe_by_xpath,
    wait_and_click,
    wait_for_element_to_disappear,
)


def expand_folder(driver, wait, folder):
    expand_btn_xpath = "./preceding-sibling::span[contains(@class, 'disclosure')]"
    expand_btn = folder.find_element(By.XPATH, expand_btn_xpath)

    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", expand_btn)
    wait.until(EC.element_to_be_clickable(expand_btn))
    expand_btn.click()


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

def find_or_create_sub_folder(driver, wait, root, parent_folder_label, sub_folder_name):
    wait_short = WebDriverWait(driver, 2)
    parent_container = parent_folder_label.find_element(By.XPATH, "./..")
    children_container = parent_container.find_element(By.XPATH, "following-sibling::*[1]")

    sub_folder = find_span_in_shadow(wait_short, children_container, sub_folder_name)
    if sub_folder:
        return sub_folder

    parent_folder_label.click()
    btn_container = _shadow_find(parent_container, wait, ".icons")
    shadow_click(btn_container, wait, "[data-action='icon-1']:nth-child(2)")
    create_folder(wait, sub_folder_name)
    # expand to make element visible
    if not has_class(children_container, 'open'):
        expand_folder(driver, wait, parent_folder_label)

    sub_folder = find_span_in_shadow(wait_short, children_container, sub_folder_name)
    return sub_folder

def select_or_create_staff_folder(driver, media_lib_url):
    parent_folder_name = 'Do Not Delete24'
    folder_name = 'Staff'
    wait = WebDriverWait(driver, WAIT.MEDIUM)
    wait_long = WebDriverWait(driver, WAIT.LONG)

    driver.get(media_lib_url)
    # Get shadow root for library tree
    sidebar_root = get_shadow_root(wait_long, '//*[@id="library-sidebar"]', 'nsemble-tree')

    parent_folder_label = find_or_create_folder(driver, wait, sidebar_root, parent_folder_name)
    expand_folder(driver, wait, parent_folder_label)

    staff_folder = find_or_create_sub_folder(driver, wait, sidebar_root, parent_folder_label, folder_name)
    scroll_and_click_element(driver, wait, staff_folder)

# Select inside staff tool
def select_staff_folder_modal(driver, wait):
    wait_and_click(wait, XPATH.staff_add_btn)
    
    # image selector 
    wait_and_click(wait, '//*[@id="cmsc-scroll-container"]/div/form/div[1]/div[1]/button')

    # switch to iframe 
    iframe = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="library-panel"]')))
    driver.switch_to.frame(iframe)

    root = get_shadow_root(wait, '//*[@id="library-sidebar"]', 'nsemble-tree')

    parent_folder_label = find_span_in_shadow(wait, root, 'Do Not Delete24')
    expand_folder(driver, wait, parent_folder_label)

    staff_folder_label = find_span_in_shadow(wait, root, 'Staff')
    scroll_and_click_element(driver, wait, staff_folder_label)

    driver.switch_to.default_content()

    # close window modal
    wait_and_click(wait,'//a[contains(@class, "ui-dialog-titlebar-close") and @role="button"]//span[contains(@class, "ui-icon-closethick")]')
    wait_and_click(wait,'//*[@id="cmsc-staff-editor-ct"]/div/div[3]/button[3]')

def upload_images(driver, local_folder):
    batch_size = 20

    # Get all image paths
    image_paths = list(Path(local_folder).glob("*.*"))  
    wait = WebDriverWait(driver, WAIT.MEDIUM)
    wait_upload = WebDriverWait(driver, WAIT.UPLOAD)

    if not image_paths:
        print("⚠️ No images found to upload.")
        return

    total = len(image_paths)
    print(f"📦 Found {total} images. Uploading in batches of {batch_size}...")

    for i in range(0, total, batch_size):
        # click on upload
        wait_and_click(wait, '//*[@id="media-library-ui-root"]/div/div/div[2]/div[1]/div[3]/nsemble-button[3]')

        batch = image_paths[i:i + batch_size]
        file_input = driver.find_element(By.ID, "files")

        print(f"💬  Uploading batch {i//batch_size + 1} ({len(batch)} files)...")
        files_to_upload = "\n".join(str(img.resolve()) for img in batch)
        file_input.send_keys(files_to_upload)

        # TODO: scroll into view  
        click_element_by_xpath(driver, wait,'//*[@id="modal-footer"]/div/div/div/div/nsemble-button')

        # wait until upload image btn dissapears (spinner)
        wait_for_element_to_disappear(wait_upload, '//*[@id="modal-footer"]/div/div/div/div/nsemble-button')

        # close
        wait_and_click(wait, '//*[@id="modal-footer"]/div/div/nsemble-button')

        print("   Completed!")

    print("✅ All images uploaded")


