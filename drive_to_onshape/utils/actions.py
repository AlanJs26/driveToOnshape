from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from typing import Union
from rich import print
from time import sleep

class Act:
    def __init__(self, driver, action, wait):
        self.driver:WebDriver = driver
        self.action:ActionChains = action
        self.wait:WebDriverWait = wait
        self.wait_little = WebDriverWait(driver, 1)

    def scroll_to_bottom(self, el:Union[str,WebElement], amount=1000, repeat=1, delay=0.5):
        if isinstance(el, str):
            for _ in range(repeat):
                self.driver.execute_script(f"document.getElementById('{el}').scrollTo(0, document.getElementById('{el}').scrollHeight)")
                sleep(delay)
            return

        scroll_origin = ScrollOrigin.from_element(el)
        actions = self.action

        for _ in range(repeat):
            actions = actions.scroll_from_origin(scroll_origin, 0, amount).pause(delay)

        actions.perform()

    def double_click(self, el):
        self.action.click(el).pause(0.2).click().pause(1).perform()

    def click(self, el):
        print(f'[green]Clicking "{el.text}"')
        self.action.click(self.wait.until(EC.element_to_be_clickable(el))).pause(1).perform()

    def right_click(self, el):
        self.action.context_click(el).pause(1).perform()
