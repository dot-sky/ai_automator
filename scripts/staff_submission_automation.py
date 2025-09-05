import json
from importlib import reload  # noqa: F401

import config.const as const_mod  # noqa: F401
import core.auth as auth_mod  # noqa: F401
import core.logger as logger_mod  # noqa: F401
import core.utils as utils_mod  # noqa: F401
import staff.media_library as media_library_mod  # noqa: F401
from config.const import MEDIA_LIB_FOLDER  #noqa: F401
from config.settings import LOCAL_IMG_FOLDER, STAFF_DATA_FILE  # noqa: F401
from core import auth, browser  # noqa: F401
from core.runner import run_step
from core.utils import (
    get_base_url,
)
from staff import staff_ops  # noqa: F401
from staff.connect import connect_to_staff_tool  # noqa: F401 
from staff.images import download_staff_images  # noqa: F401
from staff.media_library import MediaLibrary  # noqa: F401


def refresh():
    for mod in [auth_mod, const_mod, media_library_mod, utils_mod, logger_mod]:
        try:
            reload(mod)
        except Exception as e:
            print(f"[refresh] Failed to reload {mod}: {e}")
    from core.utils import get_base_url  # noqa: F401

def expand_folder(driver):
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait

    from config.const import WAIT
    from core.shadow_helpers import find_span_in_shadow, get_shadow_root
    from core.utils import switch_to_iframe_by_xpath
     

    wait =  WebDriverWait(driver, WAIT.MEDIUM)
    switch_to_iframe_by_xpath(driver, wait, '//*[@id="library-panel"]')
    root = get_shadow_root(wait, '//*[@id="library-sidebar"]', 'nsemble-tree')
    folder = find_span_in_shadow(wait, root, MEDIA_LIB_FOLDER.parent)

    expand_btn_xpath = "./preceding-sibling::span[contains(@class, 'disclosure')]"
    expand_btn = folder.find_element(By.XPATH, expand_btn_xpath)
    # check if folder is expanded
    expand_titles = expand_btn.find_elements(By.XPATH, ".//*[local-name()='svg']/*[local-name()='title']")

    if expand_titles and "open" in expand_titles[0].get_attribute("textContent").strip().lower():
        driver.switch_to.default_content()
        return

    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", expand_btn)
    wait.until(EC.element_to_be_clickable(expand_btn))
    expand_btn.click()

    driver.switch_to.default_content()


def automation_script(dealer_id, live_staff_url):        
    with open(STAFF_DATA_FILE, "r", encoding="utf-8") as file:
        staff_data = json.load(file)

    STAFF_URL = f"https://apps.dealercenter.coxautoinc.com/website/as/{dealer_id}/{dealer_id}-admin/quickLink?lang=en_US&deeplink=%2Fdealership%2Fstaff.htm"
    MEDIA_LIB_URL = f"https://apps.dealercenter.coxautoinc.com/promotions/as/{dealer_id}/{dealer_id}-admin/medialibrary3/index?lang=en_US"

    BASE_URL = get_base_url(live_staff_url) 

    driver = browser.start_driver()
    media_library = MediaLibrary(driver)

    run_step(auth.login, 
            "Login", 
            driver, STAFF_URL,
            manual_message="Log in manually in the opened browser, then type 'done' here.")

    run_step(media_library.select_or_create_staff_folder,
            "Staff Folder Creation",
            MEDIA_LIB_URL,
            manual_message=f"Create the folder '{MEDIA_LIB_FOLDER.staff}' inside '{MEDIA_LIB_FOLDER.parent}' manually and select it, then type 'done' here.")

    run_step(download_staff_images,
            "Download Staff Photos",
            driver, staff_data, BASE_URL, LOCAL_IMG_FOLDER,
            manual_message=f"Please download staff images manually into folder: {LOCAL_IMG_FOLDER}, the names of the files should be in 'NameLastName'")

    run_step(media_library.upload_images,
            "Upload Staff Photos",
            LOCAL_IMG_FOLDER,
            manual_message=f"Please upload the images manually from folder: {LOCAL_IMG_FOLDER}")

    run_step(connect_to_staff_tool,
            "Staff Tool Connection",
            driver, STAFF_URL,
            manual_message="Please connect to staff tool manually")

    departments = run_step(staff_ops.get_departments,
                        "Get Departments",
                        staff_data)

    run_step(staff_ops.submit_departments,
            "Submit Departments",
            departments, driver,
            manual_message="Submit departments manually in the staff tool, then type 'done' here.")

    run_step(staff_ops.submit_members,
            "Submit Staff Members",
            staff_data, driver, media_library,
            manual_message="Submit staff members manually in the staff tool, then type 'done' here.")

