from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from typing import Literal,List
from selenium.webdriver.common.by import By
from time import sleep
from example_package.actions import Act
from selenium.webdriver.support import expected_conditions as EC


class Onshape:
    def __init__(self, driver: WebDriver, window: str, act: Act) -> None:
        self.driver = driver
        self.window = window
        self.act = act
        self.wait = act.wait
        self.action = act.action

    def focus(self):
        self.driver.switch_to.window(self.window)

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

    def is_folder(self, el:WebElement):
        self.focus()

        aria_label = el.get_dom_attribute('aria-label')
        if not aria_label:
            return False
        return 'Folder' in aria_label

    def find_files(self, item_type: Literal['all','files','folders'] ='all', retry=0) -> List[WebElement]:
        self.focus()

        xpath = '//*[@id="document-list-scroll-container"]/table/tbody/tr/td[2]/div/div[1]/a/span'

        first_el = self.driver.find_element(By.XPATH, xpath)

        self.act.scroll_down(first_el, repeat=3)

        elems = self.driver.find_elements(By.XPATH, xpath)

        # for e in elems:
        #     print(e.text)

        if item_type == 'folders':
            elems = list(filter(lambda e: self.is_folder(e), elems))
        elif item_type == 'files':
            elems = list(filter(lambda e: not self.is_folder(e), elems))

        while retry>0 and not elems:
            seconds = 2
            print(f'[yellow]Retrying "find_in_onshape" ({seconds} seconds)...')
            sleep(seconds)
            elems = self.find_files(item_type)

        return elems

    def upload(self, file_path: str):
        if file_path.lower().endswith('.sldprt') or file_path.lower().endswith('.step') or file_path.lower().endswith('.sldasm') or file_path.lower().endswith('.slddrw'):
            print(f'[red]skipping "{file_path}"')
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
