from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from typing import Literal,List, Tuple
from selenium.webdriver.common.by import By
from time import sleep
from drive_to_onshape.utils.actions import Act
from selenium.webdriver.support import expected_conditions as EC
import re
from rich import print
from drive_to_onshape.utils.utils import TraverseException, Folder


class Onshape:
    def __init__(self, driver: WebDriver, window: str, act: Act) -> None:
        self.driver = driver
        self.window = window
        self.act = act
        self.wait = act.wait
        self.wait_little = act.wait_little
        self.action = act.action
        self.root_link = ''

    def focus(self):
        self.driver.switch_to.window(self.window)

    def go_to_path(self, path_list: List[str]):
        for path in path_list:
            folder_els, _ = self.find_files()
            for el in folder_els:
                if el.text.strip() == path:
                    self.act.click(el)
                    sleep(2)
                    break
            else:
                current_folder = Folder(path, [],[], '','')
                raise TraverseException(current_folder, f'Could not find "{current_folder.name}" element in onshape')


    def get_current_path_folders(self) -> List[str]:
        self.focus()

        def is_root(el: WebElement):
            classname = el.get_attribute('class')
            if isinstance(classname, str) and 'root' in classname:
                return True
            return False

        def parse_titles(els: List[WebElement]):
            titles = [el.get_attribute('innerText') for el in els if not is_root(el)]
            return [el.strip().split('\n')[0] for el in titles if el]

        xpath_dropdown = '/html/body/div[2]/div/div[1]/div[2]/div/span/span/os-breadcrumb/div/div/div[1]/div/ul/li'

        dropdown_els = self.driver.find_elements(By.XPATH, xpath_dropdown)

        breadcrumb_els = self.driver.find_elements(By.TAG_NAME, 'os-breadcrumb-node')

        breadcrumb_titles = parse_titles(breadcrumb_els)
        dropdown_titles = parse_titles(dropdown_els)

        return dropdown_titles + breadcrumb_titles

    def login(self, link: str):
        self.focus()
        self.driver.execute_script("document.body.style.zoom='10%'")
        self.driver.get(link)
        self.action.pause(2).send_keys(Keys.ENTER).pause(3).perform()
        self.root_link = link

    def is_folder(self, el:WebElement):
        self.focus()

        aria_label = el.get_dom_attribute('aria-label')
        if not aria_label:
            return False
        return 'Folder' in aria_label

    def find_files(self, retry=0) -> Tuple[List[WebElement], List[WebElement]]:
        self.focus()

        xpath = '//*[@id="document-list-scroll-container"]/table/tbody/tr/td[2]/div/div[1]/a/span'

        self.act.scroll_to_bottom('document-list-scroll-container', repeat=3)

        elems = self.driver.find_elements(By.XPATH, xpath)

        # for e in elems:
        #     print(e.text)

        elems = (
            list(filter(lambda e: self.is_folder(e), elems)),
            list(filter(lambda e: not self.is_folder(e), elems))
        )

        while retry>0 and not (elems[0] or elems[1]):
            seconds = 2
            print(f'[yellow]Retrying "find_in_onshape" ({seconds} seconds)...')
            sleep(seconds)
            elems = self.find_files()

        return elems

    def upload(self, file_path: str):
        if re.search(r".*\.sld.*", file_path.lower()) or file_path.lower().endswith('.step'):
            print(f'[yellow]skipping "{file_path}"')
            return
        self.focus()

        # Create button

        create_btn_xpath = '//*[@id="create-new-type"]'

        elem = self.wait.until(EC.element_to_be_clickable((By.XPATH, create_btn_xpath)))
        self.act.click(elem)

        # Import file input (Button)

        import_xpath = '//*[@id="upload-file"]'

        elem:WebElement = self.wait.until(EC.presence_of_element_located((By.XPATH, import_xpath)))
        try:
            elem.send_keys(file_path)
        except:
            print(f'[red]Could not upload "{file_path}"')

        confirm_popup_xpath = '//*[@id="model-name-dialog-ok"]'
        try:
            elem:WebElement = self.wait_little.until(EC.presence_of_element_located((By.XPATH, confirm_popup_xpath)))
            self.act.click(elem)
        except TimeoutException:
            pass


        # elem.submit()
        print(f'[blue]"{file_path}" Uploaded!')

    def make_folder(self, folder_name:str):
        self.focus()

        # Create button

        create_btn_xpath = '//*[@id="create-new-type"]'

        elem = self.wait.until(EC.element_to_be_clickable((By.XPATH, create_btn_xpath)))
        self.act.click(elem)

        # Folder dropdown button

        folder_dropdown_xpath = '/html/body/div[2]/div/div[1]/div[2]/span[1]/div/ul/li[2]/a/span'

        elem = self.wait.until(EC.element_to_be_clickable((By.XPATH, folder_dropdown_xpath)))

        self.act.click(elem)

        # Textarea

        textarea_xpath = '/html/body/div[1]/div/div/div/form/div[2]/div/div/div/input'

        elem = self.wait.until(EC.presence_of_element_located((By.XPATH, textarea_xpath)))

        elem.send_keys(folder_name)

        # Finish button

        finish_btn_xpath = '//*[@id="model-name-dialog-ok"]'

        elem = self.wait.until(EC.element_to_be_clickable((By.XPATH, finish_btn_xpath)))

        self.act.click(elem)
        sleep(2)
