import json
import os
import shutil
from importlib import reload  # noqa: F401
from pathlib import Path
from urllib.parse import urlparse

import requests
from IPython import embed
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from traitlets.config import Config
from webdriver_manager.chrome import ChromeDriverManager

import core.logger as logger_mod  # noqa: F401
import scripts.auth as auth_mod  # noqa: F401
import scripts.const as const_mod  # noqa: F401
import scripts.media_library as media_library_mod  # noqa: F401
import scripts.utils as utils_mod  # noqa: F401
from core.logger import log
from scripts import auth
from scripts.const import WAIT, XPATH
from scripts.media_library import MediaLibrary
from scripts.utils import (
    get_base_url,
    wait_and_click,
    wait_and_type,
)


# Data processing
def get_unique_departments(staff_data):
    return list(dict.fromkeys(member["department"] for member in staff_data))

def submit_departments(departments, driver):
    wait = WebDriverWait(driver, WAIT.MEDIUM)

    print("Submitting departments: ")
    for department in departments:
        try:
            wait_and_click(wait, XPATH.department_add_btn) 
            print(f" * {department}")
            wait_and_type(wait, XPATH.department_name, department.title()) 
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

def download_staff_images(staff_data, base_url, local_folder):
    if os.path.exists(local_folder):
        shutil.rmtree(local_folder)
    Path(local_folder).mkdir(parents=True, exist_ok=True)

    for member in staff_data:
        image_url = member.get("image_url", "").strip()

        if not image_url or image_url == 'N/A':
            print(f"⚠️ Skipping entry with missing name or image_url: {member.get('name')}")
            continue

        # If the URL is relative, prepend the base domain
        if image_url.startswith("/"):
            image_url = base_url.rstrip("/") + image_url

        filename = get_image_file_name(member.get("name"), image_url)

        file_path = Path(local_folder) / filename
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





def submit_staff_safe(staff_list, driver, media_library):
    wait = WebDriverWait(driver, WAIT.MEDIUM)

    def safe_send(xpath, key, default=""):
        try:
            value = staff.get(key, default)
            if value and value.strip().upper() != "N/A":
                wait_and_type(wait, xpath, value)

        except Exception as e:
            print(f"Could not fill {key}: {e}")

    media_library.select_staff_folder_modal()

    for staff in staff_list:
        try:
            log.info(f"Submitting staff member: {staff.get('name')}")
            wait_and_click(wait, XPATH.staff_add_btn)

            safe_send('//*[@id="staffName"]', "name")
            safe_send('//*[@id="staffTitle"]', "position")
            safe_send('//*[@id="staffPhone"]', "phone")
            safe_send('//*[@id="staffEmail"]', "email")
            safe_send('//*[@id="staffBio"]', "biography")

            if staff.get("image_url") != "N/A":
                media_library.select_image_modal(get_image_file_name(staff.get("name"), staff.get("image_url")))

            dept_name = staff.get("department", "").strip()
            if dept_name and dept_name.upper() != "N/A":
                dropdown_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="staffDepartment"]')))
                dropdown_btn.click()

                menu_items = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//ul[@role="listbox"]/li')))
                matched = False
                for item in menu_items:
                    if dept_name.lower() in item.text.strip().lower():
                        item.click()
                        matched = True
                        break

                if not matched:
                    log.warning(f"Department '{dept_name}' not found for {staff.get('name')}")
                    continue

            # Submit the form
            wait_and_click(wait, XPATH.submit_staff_btn)

        except Exception as e:
            log.info(f"Failed to submit staff member '{staff.get('name')}': {e}")

def start_browser_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--log-level=3")
    options.add_experimental_option("detach", True)

    # Supress chrome log messages
    service = Service(ChromeDriverManager().install(), log_path=os.devnull)
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def go_to_page(driver, url):
    driver.get(url)

def refresh():
    for mod in [auth_mod, const_mod, media_library_mod, utils_mod, logger_mod]:
        try:
            reload(mod)
        except Exception as e:
            print(f"[refresh] Failed to reload {mod}: {e}")
    from core.logger import log  # noqa: F401
    from scripts.const import WAIT, XPATH  # noqa: F401
    from scripts.media_library import MediaLibrary  # noqa: F401
    from scripts.utils import get_base_url, wait_and_click, wait_and_type  # noqa: F401



def automation_script(dealer_id, live_staff_url):        
    with open(r"output_staff.json", "r", encoding="utf-8") as file:
        staff_data = json.load(file)

    STAFF_URL = f"https://apps.dealercenter.coxautoinc.com/website/as/{dealer_id}/{dealer_id}-admin/quickLink?lang=en_US&deeplink=%2Fdealership%2Fstaff.htm"
    MEDIA_LIB_URL = f"https://apps.dealercenter.coxautoinc.com/promotions/as/{dealer_id}/{dealer_id}-admin/medialibrary3/index?lang=en_US"

    BASE_URL = get_base_url(live_staff_url) 

    LOCAL_IMG_FOLDER = "staff_images"

    driver = start_browser_driver()

    # ddc login 
    auth.login(driver, STAFF_URL)
    media_library = MediaLibrary(driver)
    # media_library.select_or_create_staff_folder(MEDIA_LIB_URL)
    # download_staff_images(staff_data, BASE_URL, LOCAL_IMG_FOLDER)     
    # media_library.upload_images(LOCAL_IMG_FOLDER) 

    # connect_staff.connect_to_staff_tool(driver, STAFF_URL)

    # departments = get_unique_departments(staff_data)
    # submit_departments(departments, driver)
    # submit_staff_safe(staff_data, driver, media_library)


    config = Config()
    config.InteractiveShellApp.extensions = ["autoreload"]
    config.InteractiveShellApp.exec_lines = ["%autoreload 2"]
    embed(config=config, banner1="🚀 Autoreload is ON. Edit & save your modules, then rerun functions.")
