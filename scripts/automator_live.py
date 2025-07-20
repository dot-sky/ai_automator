from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from IPython import embed
import time
import json

# Data processing
def get_unique_departments(staff_list):
    return list({staff["department"] for staff in staff_list})

def submit_departments(departments, driver, timeout=15):
    wait = WebDriverWait(driver, timeout)

    for department in departments:
        try:
            print(f"Submitting department: {department}")
            
            department_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cmsc-scroll-container"]/div[1]/button')))
            department_btn.click()

            # Wait for input to be ready, clear, and send keys
            input_field = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="departmentName"]')))
            input_field.clear()
            input_field.send_keys(department)

            # Wait for submit button and click
            submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cmsc-staff-editor-ct"]/div/div[3]/button[1]')))
            submit_btn.click()

        except Exception as e:
            print(f"Failed to submit department '{department}':", e)

def submit_staff(staff_list, driver, timeout=15):
    wait = WebDriverWait(driver, timeout)

    for staff in staff_list:
        try:
            print(f"Submitting staff member: {staff['Name']}")

            # Click "Add Staff" button
            staff_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cmsc-scroll-container"]/div[2]/button')))
            staff_btn.click()

            # Fill in the fields
            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="staffName"]'))).send_keys(staff["Name"])
            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="staffTitle"]'))).send_keys(staff["Position"])
            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="staffPhone"]'))).send_keys(staff["Phone"])
            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="staffEmail"]'))).send_keys(staff["Email"])
            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="staffBio"]'))).send_keys(staff["Bibliography"])

            # Select Department from dropdown
            dropdown_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="staffDepartment"]')))
            dropdown_btn.click()

            # Wait for department options to appear and select the correct one
            time.sleep(0.5)  # Allow the menu animation
            menu_items = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//ul[@role="listbox"]/li')))

            matched = False
            for item in menu_items:
                if staff["department"].strip().lower() in item.text.strip().lower():
                    item.click()
                    matched = True
                    break

            if not matched:
                print(f"Warning: Department '{staff['department']}' not found for {staff['name']}")
                continue

            # Wait until the loading indicator/button disappears (assumed behavior)
            wait.until(EC.invisibility_of_element_located((By.XPATH, '//button[@aria-label="loading"]')))

            # Submit the form
            submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cmsc-staff-editor-ct"]/div/div[3]/button[1]')))
            submit_btn.click()

            # Wait for form to close or success feedback (optional)
            time.sleep(1.5)

        except Exception as e:
            print(f"Failed to submit staff member '{staff['name']}': {e}")

def submit_staff_safe(staff_list, driver, timeout=15):
    wait = WebDriverWait(driver, timeout)

    def safe_send(xpath, key, default=""):
        """Only send value if it's not 'N/A' or missing."""
        try:
            value = staff.get(key, default)
            if value and value.strip().upper() != "N/A":
                field = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                field.clear()
                field.send_keys(value)
        except Exception as e:
            print(f"Could not fill {key}: {e}")

    for staff in staff_list:
        try:
            print(f"Submitting staff member: {staff.get('name', '[Unknown Name]')}")

            # Click "Add Staff" button
            staff_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cmsc-scroll-container"]/div[2]/button')))
            staff_btn.click()

            # Fill form fields (only if value is valid)
            safe_send('//*[@id="staffName"]', "name")
            safe_send('//*[@id="staffTitle"]', "position")
            safe_send('//*[@id="staffPhone"]', "phone")
            safe_send('//*[@id="staffEmail"]', "email")
            safe_send('//*[@id="staffBio"]', "bibliography")

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
            submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="cmsc-staff-editor-ct"]/div/div[3]/button[1]')))
            submit_btn.click()

            time.sleep(1.5)  # Optional pause to allow form to reset

        except Exception as e:
            print(f"Failed to submit staff member '{staff.get('name', '[Unknown Name]')}': {e}")

def automation_script():        
    with open("/Users/angrysp/Desktop/Mojix/hackaton/output_staff.json", "r") as file:
        staff_data = json.load(file)

    DEALER_USER_NAME = 'harganib'
    FOLDER_PROFILE_URL = "/Users/angrysp/Desktop/Mojix/hackaton/scripts/selenium-profile"

    STAFF_URL = "https://apps.dealercenter.coxautoinc.com/website/as/mojix/mojix-admin/quickLink?lang=en_US&deeplink=%2Fdealership%2Fstaff-members.htm"

    departments = list({member["department"] for member in staff_data})
    print(staff_data)
    print(departments)



    options = Options()
    options.add_argument("user-data-dir="+FOLDER_PROFILE_URL)
    options.add_argument("--remote-debugging-port=9222")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Go to page
    driver.get(STAFF_URL)
    print('page visited')
    time.sleep(2)

    # Wait for username input to appear and fill it

    def wait_and_click(wait, xpath):
        element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        element.click()

    # Log in to dealer.com
    wait = WebDriverWait(driver, 60)
    username_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="username"]')))
    username_input.clear()
    username_input.send_keys(DEALER_USER_NAME)

    # Click the Sign In button
    sign_in_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="signIn"]')))
    sign_in_button.click()

    # Log in to cox email
    enter_button = wait_and_click(wait, '//*[@id="form20"]/div[2]/input')

    # Click on the staff widget
    iframe = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="site-iframe"]')))
    driver.switch_to.frame(iframe)

    el = driver.find_element(By.XPATH, '//*[@id="staff-listing2-app-root"]')
    el.click()

    driver.switch_to.default_content()
    submit_departments(departments, driver)
    submit_staff_safe(staff_data, driver)

    embed()
    # time.sleep(10000)

    # Uncomment to test code live
