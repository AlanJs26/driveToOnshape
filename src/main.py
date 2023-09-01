from time import sleep
from typing import List, Union
from rich import print
from rich.console import Console 

from example_package.actions import Act
from example_package.utils import *

from example_package.onshape import Onshape
from example_package.google_drive import GoogleDrive

console = Console()

driver, action, wait = setup_driver()

act = Act(action, wait)



def transfer_files(drive_files:List[File], drive_folders:List[Folder], onshape_files:List[File], onshape_folders:List[Folder]):
    files:List[File] = []
    folders:List[Folder] = []

    for df in drive_folders:
        if all(f.name != df.name for f in onshape_folders):
            folders.append(df)

    for df in drive_files:
        if all(f.name != df.name for f in onshape_files):
            files.append(df)

    for folder in folders:
        onshape.make_folder(folder.name)
    # for file in files:
    #     upload_onshape(normalize_filepath(file.path))

    sleep(1)
    driver.refresh()
    sleep(3)
    print(folders) 
    print(files) 

def traverse_drive(google_drive: GoogleDrive, onshape: Onshape, current_folder: Union[Root,Folder]):
    google_drive.focus()
    sleep(0.5)

    print(f'[red]---------------------------- {current_folder.name}')

    if isinstance(current_folder, Folder):
        if current_folder.name.lower().strip() in ignore_list:
            return
        # clear_downloads()
        # if isinstance(current_folder.parent, Root):
        #     download_drive_folder(current_folder)

        folder_elems = onshape.find_files('folders')
        # print(len(folder_elems))
        # return
        el = next(filter(lambda e: e.text.lower().strip() == current_folder.name.lower().strip(), folder_elems), None)

        if el is None:

            if isinstance(current_folder.parent, Folder):
                onshape.make_folder(current_folder.name)
            sleep(1)
            driver.refresh()
            sleep(3)

            folder_elems = onshape.find_files('folders')
            el = next(filter(lambda e: e.text.lower().strip() == current_folder.name.lower().strip(), folder_elems))

        act.click(el)


        folder_elems = google_drive.find_files('folders')
        el = next(filter(lambda e: e.text.lower().strip() == current_folder.name.lower().strip(), folder_elems))

        
        act.double_click(el)
        sleep(2)

    drive_files = google_drive.find_files('files')
    files = [File(el.text, path=f'{current_folder.path}/{el.text}') for el in drive_files]

    drive_folders = google_drive.find_files('folders')
    folders = [Folder(el.text, folders=[], files=[], path=f'{current_folder.path}/{el.text}', parent=current_folder) for el in drive_folders]

    current_folder.files = files
    current_folder.folders = folders

    onshape_files = onshape.find_files('files')
    onshape_folders = onshape.find_files('folders')

    if isinstance(current_folder, Folder):
        transfer_files(
            files,
            folders,
            [File(el.text, path=f'{current_folder.path}/{el.text}') for el in onshape_files],
            [Folder(el.text, folders=[], files=[], path=f'{current_folder.path}/{el.text}', parent=current_folder) for el in onshape_folders],
        )
    # print(folders)
    # print(files)

    if folders:
        for folder in folders:
            result = traverse_drive(google_drive,onshape, folder)
            if not result:
                continue


            folder.folders = result.folders
            folder.files = result.files

    if isinstance(current_folder, Folder):
        print('[cyan]---------------------------- Going back')
        google_drive.focus()
        driver.back()
        onshape.focus()
        driver.back()
        sleep(2)

    return current_folder

# teste
# drive_link = "https://drive.google.com/drive/u/0/folders/1dS5xJgbUJ2miRvzMaXWOetXWnVEQjG9p"

# Teste
# onshape_link = "https://cad.onshape.com/documents?resourceType=resourceuserowner&nodeId=64e8f6e2cae7ec7438b71887"



# Real
drive_link = 'https://drive.google.com/drive/u/2/folders/1giaQN6A4QrPwV_VpUbnR_pRu52gGRv3V'
onshape_link = "https://cad.onshape.com/documents?nodeId=078e98a40465ff4d2fd033e4&resourceType=folder"

# Cachorro Louco
# drive_link = 'https://drive.google.com/drive/u/2/folders/1UL01NfDRiJelRY7LUOZ4mBagy2kWHf4q'
# onshape_link = "https://cad.onshape.com/documents?nodeId=dc589b28c95af8eba9e287d1&resourceType=folder"

ignore_list = [
    'jardas',
    'arena hockeys',
    'arena',
    'apolkalipse',
    'abacus',
    'abaqus',
    'arenamicromouse',
    'armagedrum',
    'atom',
    'baby bife',
    'boladinho',
    'boladinho (1)',
    'chave killtorze',
    'chave_kill',
    'copperdrum',
    'corte agua',

    'cachorro louco',
    'cachorro louco (1)',
    'chave_kill (1)',
    'duende (1)',
    'grabcad arquivos',
    'nova frente',
    "d'arc",
]

drive_window = driver.current_window_handle
# driver.switch_to.new_window('window')
# onshape_window = next(filter(lambda w: w!=drive_window, driver.window_handles))

onshape = Onshape(driver, drive_window, act) 
# google_drive = GoogleDrive(driver, drive_window, act) 

# google_drive.login('https://drive.google.com/drive/u/2/folders/1giaQN6A4QrPwV_VpUbnR_pRu52gGRv3V')
onshape.login("https://cad.onshape.com/documents?nodeId=078e98a40465ff4d2fd033e4&resourceType=folder") 

sleep(2)

file_history = Root(name='root', folders=[], files=[], path=downloads_folder)


# files_folders = find_in_onshape(driver, 'folders', retry=2)
# for ff in files_folders:
#     print(ff.text)
#
# console.rule()
#
# files_folders = find_in_drive(driver, 'folders')
# for ff in files_folders:
#     print(ff.text)

# result = traverse_drive(google_drive, onshape, file_history) 

result = onshape.get_current_path_folders()
print(result)

result = onshape.find_files('all')
print(len(result))

# download_drive_folder(Folder('primeiro', [], [], path='/'))

# click(files_folders[0])
# make_onshape_folder('jose')

# upload_onshape('/home/alan/Downloads/pcs.png')

input("press")

driver.close()
