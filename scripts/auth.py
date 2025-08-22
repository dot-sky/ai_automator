from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.logger import log
from scripts import secrets_manager
from scripts.const import WAIT, XPATH
from scripts.utils import wait_and_click, wait_and_type, wait_for_element_to_disappear


def dealer_login(wait, username):
    wait_and_type(wait, XPATH.dealer_username, username)
    wait_and_click(wait, XPATH.dealer_signin_btn)

def cox_login(wait, email, password):
    wait_and_type(wait, XPATH.cox_email, email)
    wait_and_click(wait, XPATH.cox_next_btn)

    wait_and_type(wait, XPATH.cox_password, password)
    wait_and_click(wait, XPATH.cox_submit_btn)

    wait.until(EC.element_to_be_clickable((By.XPATH, XPATH.cox_2fa_prompt)))

    log.info('Complete 2FA authentication...')

    wait_for_element_to_disappear(wait, XPATH.cox_2fa_prompt)

    wait_and_click(wait, XPATH.cox_submit_btn) 

def login(driver, url):
    wait = WebDriverWait(driver, WAIT.LONG)
    ddc_username, cox_email, cox_password = secrets_manager.load_credentials()

    driver.get(url)
    dealer_login(wait, ddc_username)
    cox_login(wait, cox_email, cox_password)

    log.success('Succesful login')