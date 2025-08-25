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

    print("Submitting departments: ")
    for department in departments:
        try:
            wait_and_click(wait, XPATH.department_add_btn) 
            log.info(f" * {department}")
            wait_and_type(wait, XPATH.department_name, department.title()) 
            wait_and_click(wait, XPATH.submit_department_btn) 

        except Exception as e:
            log.error(f"Failed to submit department '{department}':", e)

def submit_members(staff_list, driver, media_library):
    wait = WebDriverWait(driver, WAIT.MEDIUM)

    def safe_send(xpath, key, default=""):
        try:
            value = staff.get(key, default)
            if value and value.strip().upper() != "N/A":
                wait_and_type(wait, xpath, value)

        except Exception as e:
            log.warning(f"Could not fill {key}: {e}")

    media_library.select_staff_folder_modal()

    log.info("Submitting staff members:")
    for staff in staff_list:
        try:
            log.info(f"{staff.get('name')}")
            wait_and_click(wait, XPATH.staff_add_btn)

            safe_send('//*[@id="staffName"]', "name")
            safe_send('//*[@id="staffTitle"]', "position")
            safe_send('//*[@id="staffPhone"]', "phone")
            safe_send('//*[@id="staffEmail"]', "email")
            safe_send('//*[@id="staffBio"]', "biography")

            if staff.get("image_url") != "N/A":
                media_library.select_image_modal(images.get_image_file_name(staff.get("name"), staff.get("image_url")))

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

