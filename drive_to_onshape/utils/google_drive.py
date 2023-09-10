from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from typing import Literal,List, Union
from selenium.webdriver.common.by import By
from drive_to_onshape.utils.actions import Act
from selenium.webdriver.support import expected_conditions as EC
from drive_to_onshape.utils.utils import *


class GoogleDrive:
    def __init__(self, driver: WebDriver, window: str, act: Act, local_root: str) -> None:
        self.driver = driver
        self.window = window
        self.act = act
        self.wait = act.wait
        self.local_root = local_root

    def focus(self):
        self.driver.switch_to.window(self.window)

    def login(self, link: str):
        self.focus()
        self.driver.execute_script("document.body.style.zoom='10%'")
        self.driver.get(link)

    def is_folder(self, el: WebElement):
        self.focus()

        aria_label = el.find_element(By.XPATH, './../div[2]/div').get_dom_attribute('aria-label')
        if not aria_label:
            return False
        aria_label = aria_label.lower()
        return 'folder' in aria_label or 'pasta' in aria_label

    def find_files(self, item_type: Literal['all','files','folders'] ='all') -> List[WebElement]:
        self.focus()



        elem = self.driver.find_element(By.CLASS_NAME, 'a-S.a-s-tb-pa.Hb-ja-hc')



        container_id = elem.get_dom_attribute('id')

        # print(container_id)

        folder_files_xpath = f'//*[@id="{container_id}"]/div/c-wiz/div[2]/c-wiz/div[1]/c-wiz/div[2]/c-wiz/div[1]/c-wiz/c-wiz/div/c-wiz/div/div/div/div/div[4]'

        first_el = self.driver.find_element(By.XPATH, folder_files_xpath)
        self.act.scroll_to_bottom(first_el, repeat=3)

        # folder_xpath = f'//*[@id="{container_id}"]/div/c-wiz/div[2]/c-wiz/div[1]/c-wiz/div[2]/c-wiz/div[1]/c-wiz[1]/c-wiz/div/c-wiz/div/div/div/div[2]/div/div'
        # files_xpath = f'//*[@id="{container_id}"]/div/c-wiz/div[2]/c-wiz/div[1]/c-wiz/div[2]/c-wiz/div[1]/c-wiz[2]/c-wiz/div/c-wiz/div/div/div/div[2]/div/div'

        xpath = folder_files_xpath

        elems = self.driver.find_elements(By.XPATH, xpath)

        if item_type == 'folders':
            elems = list(filter(lambda e: self.is_folder(e), elems))
        elif item_type == 'files':
            elems = list(filter(lambda e: not self.is_folder(e), elems))


        return elems

    def download_folder(self, folder:Union[Root,Folder]):

        if find_folder(folder.name):
            return f'{self.local_root}/{folder.name}'

        zip_file = find_zip(folder.name)
        if zip_file:
            unzip(zip_file)
            return f'{self.local_root}/{folder.name}'

        self.focus()

        elem = self.driver.find_element(By.CLASS_NAME, 'a-S.a-s-tb-pa.Hb-ja-hc')

        container_id = elem.get_dom_attribute('id')
        print(container_id)

        folder_elems = self.find_files('folders')
        el = next(filter(lambda e: e.text == folder.name, folder_elems))

        self.act.click(el)
        
        download_btn_xpath = f'//*[@id="drive_main_page"]/div/div[5]/div[1]/div/div/div/div[2]/div/div[2]/div/div[2]/div/div[3]/div/div'

        elem = self.wait.until(EC.element_to_be_clickable((By.XPATH, download_btn_xpath)))
        self.act.click(elem)

        wait_for_downloads(folder.name)

        zip_file = find_zip(folder.name)
        if zip_file:
            unzip(zip_file)
            return f'{self.local_root}/{folder.name}'

        print(f'[red] could not download "{folder.name}"')
        return ''
