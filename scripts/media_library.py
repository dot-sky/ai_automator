from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from scripts.shadow_helpers import (
    _shadow_find,
    find_span_in_shadow,
    get_shadow_root,
    shadow_click,
    shadow_type,
)
from scripts.utils import (
    has_class,
    scroll_into_view_and_click,
    wait_and_click,
    wait_for_element_to_disappear,
)


def expand_media_lib_folder(driver, wait, folder):
    expand_btn_xpath = "./preceding-sibling::span[contains(@class, 'disclosure')]"
    expand_btn = folder.find_element(By.XPATH, expand_btn_xpath)

    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", expand_btn)
    wait.until(EC.element_to_be_clickable(expand_btn))
    expand_btn.click()


def create_folder(wait, folder_name):
    modal_root = get_shadow_root(wait, '//*[@id="modal-window"]', '#modal-body > div > div > nsemble-input')

    shadow_type(modal_root, wait, '#label', folder_name)
    wait_and_click(wait, '//*[@id="modal-footer"]/div/div/div/nsemble-button')

    wait_for_element_to_disappear(wait, '//*[@id="modal-window"]')

def find_or_create_folder(driver, wait, root, folder_name):
    wait_short = WebDriverWait(driver, 2)
    folder_label = find_span_in_shadow(wait_short, root, folder_name)
    if folder_label:
        return folder_label

    print(f'LOG: Folder "{folder_name}" not found, creating...')

    wait_and_click(wait, '//*[@id="library-sidebar"]/div/div[2]/div/div[1]/nsemble-button')
    create_folder(wait, folder_name)

    folder_label = find_span_in_shadow(wait_short, root, folder_name)

    return folder_label

def find_or_create_sub_folder(driver, wait, root, parent_folder_label, folder_name):
    wait_short = WebDriverWait(driver, 2)
    parent_container = parent_folder_label.find_element(By.XPATH, "./..")
    children_container = parent_container.find_element(By.XPATH, "following-sibling::*[1]")

    sub_folder = find_span_in_shadow(wait_short, children_container, folder_name)
    if sub_folder:
        return sub_folder

    parent_folder_label.click()
    btn_container = _shadow_find(parent_container, wait, ".icons")
    shadow_click(btn_container, wait, "[data-action='icon-1']:nth-child(2)")
    create_folder(wait, folder_name)

    sub_folder = find_span_in_shadow(wait_short, root, folder_name)

    return sub_folder



# --- Main function ---

def select_or_create_media_lib_folder(driver, wait, media_lib_url):
    parent_folder_name = 'Do Not Delete24'
    folder_name = 'Staff'

    driver.get(media_lib_url)

    # Get shadow root for library tree
    sidebar_root = get_shadow_root(wait, '//*[@id="library-sidebar"]', 'nsemble-tree')

    # Parent Folder
    parent_folder_label = find_or_create_folder(driver, wait, sidebar_root, parent_folder_name)
    expand_media_lib_folder(driver, wait, parent_folder_label)

    # --- Child folder ---
    staff_folder = find_or_create_sub_folder(driver, wait, sidebar_root, parent_folder_label, folder_name)

    # Expand if necessary
    parent_container = parent_folder_label.find_element(By.XPATH, "./..")
    children_container = parent_container.find_element(By.XPATH, "following-sibling::*[1]")
    if not has_class(children_container, 'open'):
        expand_media_lib_folder(driver, wait, parent_folder_label)

    # Click the staff folder
    scroll_into_view_and_click(driver, wait, staff_folder)

    print(f'LOG: Folder "{folder_name}" clicked successfully!')
