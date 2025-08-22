from urllib.parse import urlparse

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def wait_and_click(wait, xpath):
    element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
    element.click()

def wait_and_type(wait, xpath, text):
    element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
    element.clear()
    element.send_keys(text)

def find_by_xpath_and_click(driver, wait, xpath):
    element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    scroll_into_view_and_click(driver, wait, element)

def scroll_into_view_and_click(driver, wait, element):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
    wait.until(EC.element_to_be_clickable(element)).click()

def wait_for_element_to_disappear(wait, xpath):
    try:
        wait.until(EC.invisibility_of_element_located((By.XPATH, xpath)))
        return True
    except TimeoutException:
        print(f"⚠️ Timeout: Element '{xpath}' didn't dissapear.")
        return False

def has_class(element, class_name):
    return class_name in element.get_attribute('class').split()

def get_base_url(url: str) -> str:
    """
    Extracts the base URL (scheme + domain) from a given URL.
    """

    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"