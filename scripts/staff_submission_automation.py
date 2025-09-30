import json
from importlib import reload

import config.const as const_mod
import core.auth as auth_mod
import core.logger as logger_mod
import core.utils as utils_mod
import staff.media_library as media_library_mod
from config.const import MEDIA_LIB_FOLDER
from config.settings import LOCAL_IMG_FOLDER, STAFF_DATA_FILE
from core import auth, browser
from core.runner import run_step
from core.utils import (
    get_base_url,
)
from staff import staff_ops
from staff.connect import connect_to_staff_tool
from staff.images import download_staff_images
from staff.media_library import MediaLibrary


def refresh():
    for mod in [auth_mod, const_mod, media_library_mod, utils_mod, logger_mod]:
        try:
            reload(mod)
        except Exception as e:
            print(f"[refresh] Failed to reload {mod}: {e}")

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

