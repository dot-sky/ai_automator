from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from scripts.const import XPATH, WAIT
from scripts.utils import wait_and_click

def start_staff_widget(driver, wait_short, wait_long):
    iframe = wait_long.until(
        EC.element_to_be_clickable((By.XPATH, XPATH.staff_iframe))
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

def connect_to_staff_tool(driver):
    print("> Starting staff widget tool ...")
    wait_long = WebDriverWait(driver, WAIT.LONG)
    wait_short = WebDriverWait(driver, WAIT.SHORT)

    attempt = 0
    while True:
        attempt += 1
        print(f"> Connecting to tool ({attempt})")

        # Step 1: Start the staff widget
        start_staff_widget(driver, wait_long, wait_short)

        # Step 2: Wait for either error or success
        try:
            result = wait_long.until(wait_for_either_element)
        except TimeoutException:
            print("Timed out waiting for staff tool to load.")
            return

        # Step 3: Handle outcomes
        if result == "error":
            print("⚠️ Error: please connect to a US VPN.")
            answer = input("     Press 'y' and Enter when connected: ").strip().lower()
            if answer != 'y':
                print("Aborting connection.")
                return

            # Close the error modal
            try:
                wait_and_click(wait_short, XPATH.staff_error_close_btn)

                # Wait until modal disappears
                wait_short.until(
                    EC.invisibility_of_element_located((By.XPATH, XPATH.staff_error_close_btn))
                )
            except TimeoutException:
                print("Close button did not disappear — aborting.")
                return

            # Retry
            continue

        elif result == "success":
            print("✅ Connected to staff tool.")
            print("⚠️ Disable VPN")
            answer = input("     Press 'y' and Enter when disabled: ").strip().lower()
            if answer != 'y':
                print("Aborting connection.")
                return

            return