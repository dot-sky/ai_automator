from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def find_span_in_shadow(wait, root, text):
    def _search(_driver):
            spans = root.find_elements(By.CSS_SELECTOR, "span.label")
            return next((s for s in spans if s.text.strip().lower() == text.strip().lower()), None)
    try:
        return wait.until(_search)
    except TimeoutException:
        return None

def _shadow_find(root, wait, css_selector):
    def _find(_):
        return root.find_element(By.CSS_SELECTOR, css_selector)
    try: 
        return wait.until(_find)
    except TimeoutException:
        print(f"Element with selector '{css_selector}' was not found in the shadow root.")
        raise

def shadow_type(root, wait, css_selector, text):
    element = _shadow_find(root, wait, css_selector)
    wait.until(EC.element_to_be_clickable(element))
    element.clear()
    element.send_keys(text)

def shadow_click(root, wait, css_selector):
    element = _shadow_find(root, wait, css_selector)
    wait.until(EC.element_to_be_clickable(element))
    element.click()

def get_shadow_root(wait, container_xpath, shadow_element_css):
    container = wait.until(EC.presence_of_element_located((By.XPATH, container_xpath)))
    host = container.find_element(By.CSS_SELECTOR, shadow_element_css)
    root = host.shadow_root
    return root
