from time import sleep
import json

from drive_to_onshape.main import *

# Opening JSON file
with open('config.json', 'r') as file:
    config = json.load(file)


ignore_list_local = config['ignore_list_local']

ignore_list = config['ignore_list']


ignore_list_local = [e.lower().strip() for e in ignore_list_local]
ignore_list = [e.lower().strip() for e in ignore_list]

drive_window = driver.current_window_handle
driver.switch_to.new_window('window')
onshape_window = next(filter(lambda w: w!=drive_window, driver.window_handles))

onshape = Onshape(driver, onshape_window, act) 
google_drive = GoogleDrive(driver, drive_window, act, local_root = downloads_folder) 

google_drive.login(config['drive_root_link'])
onshape.login(config['onshape_root_link']) 


sleep(2)


result = traverse_drive(google_drive, onshape, ignore_list, ignore_list_local) 

input("press")

driver.close()
