from pathlib import Path

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.logger import log
from scripts.const import MEDIA_LIB_FOLDER, WAIT, XPATH
from scripts.shadow_helpers import (
    _shadow_find,
    find_span_in_shadow,
    get_shadow_root,
    shadow_click,
    shadow_type,
)
from scripts.utils import (
    click_element_by_xpath,
    has_class,
    scroll_and_click_element,
    scroll_element_into_view,
    switch_to_iframe_by_xpath,
    wait_and_click,
    wait_for_element_to_disappear,
)


class MediaLibrary:
    def __init__(self, driver):
        self.driver = driver
        self.wait_extra_short = WebDriverWait(driver, WAIT.SHORT)
        self.wait =  WebDriverWait(driver, WAIT.MEDIUM)
        self.wait_long = WebDriverWait(driver, WAIT.LONG)
        self.wait_upload = WebDriverWait(driver, WAIT.UPLOAD)

    # Folder helpers
    def expand_folder(self, folder):
        expand_btn_xpath = "./preceding-sibling::span[contains(@class, 'disclosure')]"
        expand_btn = folder.find_element(By.XPATH, expand_btn_xpath)

        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", expand_btn)
        self.wait.until(EC.element_to_be_clickable(expand_btn))
        expand_btn.click()

    def create_folder(self, folder_name):
        modal_root = get_shadow_root(self.wait, '//*[@id="modal-window"]', '#modal-body > div > div > nsemble-input')

        shadow_type(modal_root, self.wait, '#label', folder_name)
        wait_and_click(self.wait, '//*[@id="modal-footer"]/div/div/div/nsemble-button')

        wait_for_element_to_disappear(self.wait, '//*[@id="modal-window"]')

    def find_or_create_folder(self, root, folder_name):
        folder_label = find_span_in_shadow(self.wait_extra_short, root, folder_name)
        if folder_label:
            return folder_label

        log.warning('Creating folder "{folder_name}"...')
        wait_and_click(self.wait, '//*[@id="library-sidebar"]/div/div[2]/div/div[1]/nsemble-button')
        self.create_folder(self.wait, folder_name)

        folder_label = find_span_in_shadow(self.wait_extra_short, root, folder_name)

        return folder_label

    def find_or_create_sub_folder(self, parent_folder_label, sub_folder_name):
        parent_container = parent_folder_label.find_element(By.XPATH, "./..")
        children_container = parent_container.find_element(By.XPATH, "following-sibling::*[1]")

        sub_folder = find_span_in_shadow(self.wait_extra_short, children_container, sub_folder_name)
        if sub_folder:
            return sub_folder

        log.warning('Creating folder "{sub_folder_name}"...')
        parent_folder_label.click()
        btn_container = _shadow_find(parent_container, self.wait, ".icons")
        shadow_click(btn_container, self.wait, "[data-action='icon-1']:nth-child(2)")
        self.create_folder(self.wait, sub_folder_name)

        # expand to make element visible
        if not has_class(children_container, 'open'):
            self.expand_folder(parent_folder_label)

        sub_folder = find_span_in_shadow(self.wait_extra_short, children_container, sub_folder_name)
        return sub_folder

    def select_or_create_staff_folder(self, driver, media_lib_url):
        driver.get(media_lib_url)
        # Get shadow root for library tree
        sidebar_root = get_shadow_root(self.wait_long, '//*[@id="library-sidebar"]', 'nsemble-tree')

        parent_folder_label = self.find_or_create_folder(driver, self.wait, sidebar_root, MEDIA_LIB_FOLDER.parent)
        self.expand_folder(driver, self.wait, parent_folder_label)

        staff_folder = self.find_or_create_sub_folder(driver, self.wait, sidebar_root, parent_folder_label, MEDIA_LIB_FOLDER.staff)
        scroll_and_click_element(driver, self.wait, staff_folder)

    # Select inside staff tool
    def select_staff_folder_modal(self):
        wait_and_click(self.wait, XPATH.staff_add_btn)
    
        # image selector 
        wait_and_click(self.wait, '//*[@id="cmsc-scroll-container"]/div/form/div[1]/div[1]/button')

        # switch to iframe 
        switch_to_iframe_by_xpath(self.driver, self.wait, '//*[@id="library-panel"]')

        root = get_shadow_root(self.wait, '//*[@id="library-sidebar"]', 'nsemble-tree')

        parent_folder_label = find_span_in_shadow(self.wait, root, 'Do Not Delete24')
        self.expand_folder(self.driver, self.wait, parent_folder_label)

        staff_folder_label = find_span_in_shadow(self.wait, root, 'Staff')
        scroll_and_click_element(self.driver, self.wait, staff_folder_label)

        self.driver.switch_to.default_content()

        # close window modal
        wait_and_click(self.wait,'//a[contains(@class, "ui-dialog-titlebar-close") and @role="button"]//span[contains(@class, "ui-icon-closethick")]')
        wait_and_click(self.wait,'//*[@id="cmsc-staff-editor-ct"]/div/div[3]/button[3]')

    def upload_images(self, local_folder, batch_size=20):
        image_paths = list(Path(local_folder).glob("*.*"))

        if not image_paths:
            log.warning(f"No images found in {local_folder}")
            return

        total = len(image_paths)
        log.info(f"📦 Found {total} images. Uploading in batches of {batch_size}...")

        for i in range(0, total, batch_size):
            wait_and_click(self.wait, '//*[@id="media-library-ui-root"]/div/div/div[2]/div[1]/div[3]/nsemble-button[3]')
            batch = image_paths[i:i + batch_size]
            file_input = self.driver.find_element(By.ID, "files")

            log.info(f"Uploading batch {i//batch_size + 1} ({len(batch)} files)...")
            file_input.send_keys("\n".join(str(img.resolve()) for img in batch))

            click_element_by_xpath(self.driver, self.wait,'//*[@id="modal-footer"]/div/div/div/div/nsemble-button')
            wait_for_element_to_disappear(self.wait_upload, '//*[@id="modal-footer"]/div/div/div/div/nsemble-button')
            wait_and_click(self.wait, '//*[@id="modal-footer"]/div/div/nsemble-button')

            log.success(f"Batch {i//batch_size + 1} completed.")

        log.success("All images uploaded.")

    def select_image_modal(self, file_name):
        wait_and_click(self.wait, '//*[@id="cmsc-scroll-container"]/div/form/div[1]/div[1]/button')
        switch_to_iframe_by_xpath(self.driver, self.wait, '//*[@id="library-panel"]')

        image = None
        while not image:
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#media-library-ui-root .grid-view")))
            elements = self.driver.find_elements(By.XPATH, f"//span[@class='file-name' and text()='{file_name}']")
            if elements:
                image = elements[0]
                scroll_element_into_view(self.driver, self.wait, image)
                break

            # Go to next page
            next_buttons = self.driver.find_elements(By.XPATH, "//ul[@class='nsemble-pagination']/li[@class='next']")
            if next_buttons and "disabled" not in next_buttons[0].get_attribute("class"):
                scroll_and_click_element(self.driver, self.wait, next_buttons[0])
                self.wait.until(EC.staleness_of(next_buttons[0]))
            else:
                log.warning(f"Image '{file_name}' not found in media library.")
                wait_and_click(self.wait, '//a[contains(@class, "ui-dialog-titlebar-close")]')
                wait_and_click(self.wait, '//*[@id="cmsc-staff-editor-ct"]/div/div[3]/button[3]')
                self.driver.switch_to.default_content()
                return

        ActionChains(self.driver).double_click(image).perform()
        self.driver.switch_to.default_content()