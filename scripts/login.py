from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from scripts import utils
from scripts.const import WAIT, XPATH
from scripts.secrets_manager import get_or_set_password, get_or_set_username


def staff_tool_login(driver, staff_url):
    wait = WebDriverWait(driver, WAIT.LONG)

    # Load credentials
    ddc_username = get_or_set_username('ddc')
    cox_email = get_or_set_username('cox')
    cox_password = get_or_set_password('cox', cox_email)

    # 1. Go to page
    driver.get(staff_url)
    
    # 2. Dealer.com login
    utils.wait_and_type(wait, XPATH.dealer_username, ddc_username)
    utils.wait_and_click(wait, XPATH.dealer_signin_btn)

    # 3. Cox login
    utils.wait_and_type(wait, XPATH.cox_email, cox_email)
    utils.wait_and_click(wait, XPATH.cox_next_btn)

    utils.wait_and_type(wait, XPATH.cox_password, cox_password)
    utils.wait_and_click(wait, XPATH.cox_submit_btn)

    # 4 Handle 2FA 
    wait.until(EC.element_to_be_clickable((By.XPATH, XPATH.cox_2fa_prompt)))

    print('Complete 2FA authentication...')
    utils.wait_for_element_to_disappear(wait, XPATH.cox_2fa_prompt)

    utils.wait_and_click(wait, XPATH.cox_submit_btn) 
    
    iframe = wait.until(EC.presence_of_element_located((By.XPATH, XPATH.staff_iframe)))

    print("✅ Login sequence completed.")