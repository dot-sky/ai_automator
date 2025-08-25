from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.const import WAIT, XPATH
from core.utils import wait_and_click


def start_staff_widget(driver, wait_short, wait_long):
    iframe = wait_long.until(
        EC.presence_of_element_located((By.XPATH, XPATH.staff_iframe))
    )
    driver.switch_to.frame(iframe)

    wait_and_click(wait_short, XPATH.staff_widget)

    driver.switch_to.default_content()

def wait_for_either_element(driver):
    error_elements = driver.find_elements(By.XPATH, XPATH.staff_error_msg)
    if error_elements and error_elements[0].text.strip() == '⚠ Error':
        return "error"

    success_elements = driver.find_elements(By.XPATH, XPATH.staff_add_btn)
    if success_elements:
        return "success"

    return False

def connect_to_staff_tool(driver, staff_url):
    print("> Starting staff widget tool ...")

    wait_long = WebDriverWait(driver, WAIT.EXTRA_LONG)
    wait = WebDriverWait(driver, WAIT.MEDIUM)

    driver.get(staff_url)

    attempt = 0
    while True:
        attempt += 1
        print(f"> Connecting to tool ({attempt})")
        start_staff_widget(driver, wait_long, wait)

        # Step 2: Wait for either error or success
        try:
            result = wait_long.until(wait_for_either_element)
        except TimeoutException:
            print("Timed out waiting for staff tool to load.")
            return

        # Step 3: Handle outcomes
        if result == "error":
            print("⚠️  Error: please connect to a US VPN.")
            answer = input("     Press 'y' and Enter when connected: ").strip().lower()
            if answer != 'y':
                print("Aborting connection.")
                return

            # Close the error modal
            try:
                wait_and_click(wait, XPATH.staff_error_close_btn)

                # Wait until modal disappears
                wait.until(
                    EC.invisibility_of_element_located((By.XPATH, XPATH.staff_error_close_btn))
                )
            except TimeoutException:
                print("Close button did not disappear — aborting.")
                return

            # Retry
            continue

        elif result == "success":
            print("✅ Connected to staff tool.")
            print("⚠️  Disable VPN")
            answer = input("     Press 'y' and Enter when disabled: ").strip().lower()
            if answer != 'y':
                print("Aborting connection.")
                return

            return