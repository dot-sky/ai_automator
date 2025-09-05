import os
import shutil
from urllib.parse import urlparse

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def wait_and_click(wait, xpath):
    element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
    element.click()

def wait_and_type(wait, xpath, text):
    element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
    element.clear()
    element.send_keys(text)

def click_element_by_xpath(driver, wait, xpath):
    element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    scroll_and_click_element(driver, wait, element)
    return element

def scroll_and_click_element(driver, wait, element):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
    wait.until(EC.element_to_be_clickable(element)).click()

def scroll_xpath_into_view(driver, wait, xpath):
    element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    scroll_element_into_view(driver, wait, element)
    return element

def scroll_element_into_view(driver, wait, element):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
    wait.until(EC.element_to_be_clickable(element))

def wait_for_element_to_disappear(wait, xpath):
    wait.until(EC.invisibility_of_element_located((By.XPATH, xpath)))

def switch_to_iframe_by_xpath(driver, wait, xpath):
    iframe = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    driver.switch_to.frame(iframe)
    return iframe

def has_class(element, class_name):
    return class_name in element.get_attribute('class').split()

def get_base_url(url):
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"

def ensure_path(path, clean=False):
    if os.path.splitext(path)[1]:
        folder = os.path.dirname(path) or path
    else:
        folder = path

    if clean and os.path.exists(folder):
        shutil.rmtree(path)
    
    os.makedirs(folder, exist_ok=True)

    return path