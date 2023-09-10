import os
import shutil
import re
from time import sleep
from dataclasses import dataclass
from typing import List, Optional, Union
from rich import print
from datetime import datetime

import subprocess, functools

from selenium import webdriver
import selenium.webdriver.common.service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains

@dataclass
class Root:
    name: str
    folders: 'List[Folder]'
    files: 'List[File]'
    remote_path: str = ''
    local_path: str = ''
    onshape_link: str = ''
    parent = None

@dataclass
class File:
    name: str
    remote_path: str = ''
    local_path: str = ''

@dataclass
class Folder:
    name: str
    folders: 'List[Folder]'
    files: 'List[File]'
    remote_path: str
    local_path: str
    parent: 'Optional[Folder|Root]' = None
    onshape_link: str = ''

class TraverseException(Exception):
    def __init__(self, folder: Union[Folder,Root], message: str):
        self.folder = folder
        self.message = message
        super().__init__(self.message)


downloads_folder = "/home/alan/Downloads"
log_file = f'log-{datetime.now()}.json'

def ignore_exceptions(fallback=None, exceptions=(Exception,)):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions:
                return fallback
        return wrapper
    return decorator

def listdir(path: str):
    dirs, files = split_files_folders(os.listdir(path), path)
    def sortAZ(arr):
        return sorted(arr, key=lambda s: s.lower())

    return sortAZ(dirs), sortAZ(files)

def split_files_folders(mixedfiles: List[str], root):
    folders = []
    files = []

    for f in mixedfiles:
        if os.path.isfile(os.path.join(root, f)):
            files.append(f)
            continue
        folders.append(f)

    return folders, files

def new_start(*args, **kwargs):
    def preexec_function():
        # signal.signal(signal.SIGINT, signal.SIG_IGN) # this one didn't worked for me
        os.setpgrp()
    default_Popen = subprocess.Popen
    subprocess.Popen = functools.partial(subprocess.Popen, preexec_fn=preexec_function)
    try:
        new_start.default_start(*args, **kwargs)
    finally:
        subprocess.Popen = default_Popen

def setup_driver():
    new_start.default_start = selenium.webdriver.common.service.Service.start

    selenium.webdriver.common.service.Service.start = new_start

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
        match = re.search(r'(^.+)-[A-Z0-9]+-[0-9]+\.zip', filename)
        if match and match.groups()[0] == folder_name:
            if verbose:
                print(f'[blue]Found "{filename}" in downloads folder')
            return filename

    return '' 

def intersect(a_list:List[str], b_list:List[str]):
    first_diff_index = 0
    a_list = list(filter(str, a_list))
    b_list = list(filter(str, b_list))

    if len(a_list) > len(b_list):
        zipped_lists = zip(b_list, a_list[0:len(b_list)])
    else:
        zipped_lists = zip(a_list, b_list[0:len(a_list)])
    
    for a,b in zipped_lists:
        if a != b:
            break
        first_diff_index += 1
        
    return a_list[first_diff_index:], b_list[first_diff_index:]

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
