from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.const import WAIT, XPATH
from core.logger import log
from core.utils import (
    wait_and_click,
    wait_and_type,
)
from staff import images


def get_departments(staff_data):
    return list(dict.fromkeys(member["department"] for member in staff_data))

def submit_departments(departments, driver):
    wait = WebDriverWait(driver, WAIT.MEDIUM)

    log.title("Submitting departments:")
    log.info(f"Found {len(departments)} unique departments")

    for department in departments:
        try:
            wait_and_click(wait, XPATH.department_add_btn) 
            wait_and_type(wait, XPATH.department_name, department.title()) 
            wait_and_click(wait, XPATH.submit_department_btn) 
            log.success(f"{department}",indent=1)

        except Exception as e:
            log.error(f"Failed to submit department '{department}':", e)
    log.success('Departments submitted successfully')
    log.end_title()

def safe_write(wait, staff, key, xpath):
    try:
        value = staff.get(key)
        if value and value.strip().upper() != "N/A":
            wait_and_type(wait, xpath, value)

    except Exception as e:
        log.warning(f"Could not fill {key}: {e}")

def select_department(wait, staff):
    dept_name = staff.get("department", "").strip()
    if not dept_name or dept_name.upper() == "N/A":
        return False

    wait_and_click(wait, '//*[@id="staffDepartment"]')
    menu_items = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//ul[@role="listbox"]/li')))

    for item in menu_items:
        if dept_name.lower() in item.text.strip().lower():
            item.click()
            return True

    log.error(f"Could not select department '{dept_name}'")       
    return False

def submit_one_member(wait, staff, media_library):
    wait_and_click(wait, XPATH.staff_add_btn)

    fields = {
    "name": '//*[@id="staffName"]',
    "position": '//*[@id="staffTitle"]',
    "phone": '//*[@id="staffPhone"]',
    "email": '//*[@id="staffEmail"]',
    "biography": '//*[@id="staffBio"]'
    }

    for key, xpath in fields.items():
        safe_write(wait, staff, key, xpath)

    image_url = staff.get("image_url", "N/A")
    if image_url != "N/A":
        filename = images.get_image_file_name(staff.get("name"), image_url)
        media_library.select_image_modal(filename)
    
    select_department(wait, staff)

    wait_and_click(wait, XPATH.submit_staff_btn)

def submit_members(staff_list, driver, media_library):
    wait = WebDriverWait(driver, WAIT.MEDIUM)
    media_library.select_staff_folder_modal()

    log.title("Submitting staff members:")
    log.info(f"Found {len(staff_list)} staff members")
    for staff in staff_list:
        try:
            submit_one_member(wait, staff, media_library)
            log.success(f"{staff.get('name')}", indent=1)
        except Exception as e:
            log.error(f"Failed to submit staff member '{staff.get('name')}': {e}")

    log.success("All staff members submitted successfully")
    log.end_title()
