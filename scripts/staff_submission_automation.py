import json
from importlib import reload  # noqa: F401

from IPython import embed
from traitlets.config import Config

import config.const as const_mod  # noqa: F401
import core.auth as auth_mod  # noqa: F401
import core.logger as logger_mod  # noqa: F401
import core.utils as utils_mod  # noqa: F401
import staff.media_library as media_library_mod  # noqa: F401
from config.settings import LOCAL_IMG_FOLDER  # noqa: F401
from core import auth, browser
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



def automation_script(dealer_id, live_staff_url):        
    with open(r"output_staff.json", "r", encoding="utf-8") as file:
        staff_data = json.load(file)

    STAFF_URL = f"https://apps.dealercenter.coxautoinc.com/website/as/{dealer_id}/{dealer_id}-admin/quickLink?lang=en_US&deeplink=%2Fdealership%2Fstaff.htm"
    MEDIA_LIB_URL = f"https://apps.dealercenter.coxautoinc.com/promotions/as/{dealer_id}/{dealer_id}-admin/medialibrary3/index?lang=en_US"

    BASE_URL = get_base_url(live_staff_url) 


    driver = browser.start_driver()

    # ddc login 
    auth.login(driver, STAFF_URL)
    media_library = MediaLibrary(driver)
    media_library.select_or_create_staff_folder(MEDIA_LIB_URL)
    download_staff_images(staff_data, BASE_URL, LOCAL_IMG_FOLDER)     
    media_library.upload_images(LOCAL_IMG_FOLDER) 

    connect_to_staff_tool(driver, STAFF_URL)

    departments = staff_ops.get_departments(staff_data)
    staff_ops.submit_departments(departments, driver)
    staff_ops.submit_members(staff_data, driver, media_library)

    config = Config()
    config.InteractiveShellApp.extensions = ["autoreload"]
    config.InteractiveShellApp.exec_lines = ["%autoreload 2"]
    embed(config=config, banner1="🚀 Autoreload is ON. Edit & save your modules, then rerun functions.")
