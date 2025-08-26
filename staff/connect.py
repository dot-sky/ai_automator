from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.const import WAIT, XPATH
from core.logger import log
from core.prompter import prompter
from core.utils import wait_and_click


def move_mouse(driver, xpath):
    element = driver.find_element(By.XPATH, xpath)
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()

def start_staff_widget(driver, wait_short, wait_long):
    # hover to reset overlay of tool
    move_mouse(driver, '//*[@id="internal-tools-select"]')

    iframe = wait_long.until(EC.presence_of_element_located((By.XPATH, XPATH.staff_iframe)))
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
    log.title("Starting Staff Widget Tool...")

    wait_long = WebDriverWait(driver, WAIT.EXTRA_LONG)
    wait = WebDriverWait(driver, WAIT.MEDIUM)
    driver.get(staff_url)

    attempt = 0
    while True:
        attempt += 1
        if attempt == 1:
            log.info("Connecting to staff tool")
        else:
            log.info(f"Retrying connection (attempt {attempt})")

        start_staff_widget(driver, wait_long, wait)

        try:
            result = wait_long.until(wait_for_either_element)
        except TimeoutException:
            log.error("Timed out waiting for staff tool to load.")
            log.end_title()
            return

        if result == "error":
            log.warning("A US VPN connection is required.")
            answer = prompter.ask_yes_no("Connect to a US VPN, then press 'y' and Enter", indent=2)
            if not answer:
                log.error("Aborting connection.")
                log.end_title()
                return
            try:
                wait_and_click(wait, XPATH.staff_error_close_btn)
                wait.until(EC.invisibility_of_element_located((By.XPATH, XPATH.staff_error_close_btn)))
            except TimeoutException:
                log.error("Close button did not disappear — aborting.")
                log.end_title()
                return
            continue # Retry

        elif result == "success":
            log.success("Successfully connected to staff tool.")
            log.warning("VPN must now be disabled for the next step.")
            answer = prompter.ask_yes_no("Disable your VPN, then press 'y' and Enter", indent=2)
            if not answer:
                log.error("Aborting connection.")
                log.end_title()
                return
            log.success("VPN disabled. Continuing...")
            log.end_title()
            return