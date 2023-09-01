import os
import shutil
import re
from time import sleep
from dataclasses import dataclass
from typing import List, Optional
from rich import print

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

@dataclass
class Root:
    name: str
    folders: 'List[Folder]'
    files: 'List[File]'
    path: str = '/'
    onshape_link: str = ''

@dataclass
class File:
    name: str
    path: str

@dataclass
class Folder:
    name: str
    folders: 'List[Folder]'
    files: 'List[File]'
    path: str
    parent: 'Optional[Folder|Root]' = None
    onshape_link: str = ''


downloads_folder = "/home/alan/Downloads"

def normalize_filepath(filepath):
    folder_path, basename = os.path.split(filepath)

    for filename in os.listdir(folder_path):
        if os.path.isfile(os.path.join(folder_path, filename)):
            if os.path.splitext(filename)[0] == os.path.splitext(basename)[0]:
                return os.path.join(folder_path, filename)

    return filepath



def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('test-type')
    options.add_argument("disable-infobars");
    options.add_argument('--user-data-dir=/home/alan/.config/google-chrome')

    driver = webdriver.Chrome(options=options)
    action = ActionChains(driver)
    wait = WebDriverWait(driver, 10)

    return driver, action, wait

def unzip(zip_name):
    print('[blue]unziping "{zip_name}"')
    os.system(f'unzip "{downloads_folder}/{zip_name}" -d "{downloads_folder}"')

def find_folder(folder_name):
    for filename in os.listdir(downloads_folder):
        if filename == folder_name:
            print(f'[blue]Found "{folder_name}" in downloads folder')
            return filename

    return '' 
def find_zip(folder_name, verbose=True):
    for filename in os.listdir(downloads_folder):
        if re.search(rf'{folder_name}-.*\.zip', filename):
            if verbose:
                print(f'[blue]Found "{filename}" in downloads folder')
            return filename

    return '' 

def clear_downloads():
    print('[blue]Clearing downloads folder')
    for root, dirs, files in os.walk(downloads_folder):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))
def wait_for_downloads(folder_name):
    print(f'[blue]Waiting for "{folder_name}" zip download')
    while (
        not os.listdir(downloads_folder) or 
        not find_zip(folder_name, verbose=False) or 
            any(filename.endswith(".crdownload") for filename in os.listdir(downloads_folder))
    ):
        sleep(2)
        print(".", end="")
    print("\n[blue]done!")
