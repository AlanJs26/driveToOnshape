from time import sleep
from typing import List, Union
from rich import print
from rich.console import Console 
import json
import traceback
from copy import copy

from drive_to_onshape.utils.actions import Act
from drive_to_onshape.utils.utils import *

from drive_to_onshape.utils.onshape import Onshape
from drive_to_onshape.utils.google_drive import GoogleDrive
from dataclasses import is_dataclass

console = Console()

driver, action, wait = setup_driver()

act = Act(driver, action, wait)

def transfer_files(onshape: Onshape, local_folders:List[str], local_files:List[str], onshape_folders:List[str], onshape_files:List[str], root:str):
    files:List[str] = []
    folders:List[str] = []

    for df in local_folders:
        if all(f != df for f in onshape_folders):
            folders.append(df)

    for df in local_files:
        if all(f != df for f in onshape_files):
            files.append(df)

    for folder in folders:
        onshape.make_folder(folder)
    for file in files:
        onshape.upload(os.path.join(root,file))

    if files or folders:
        print('[blue]Transfering folders and files')
        print(folders) 
        print(files) 
        if files:
            sleep(2)
        else:
            sleep(1)
        driver.refresh()
        sleep(3)

# @ignore_exceptions(fallback=Folder('none', [], [], remote_path='', local_path=''), exceptions=(KeyboardInterrupt,))
def traverse_local(google_drive: GoogleDrive, onshape: Onshape, current_folder: Union[Root,Folder], ignore_list_local:List[str]=[]) -> Union[Folder,Root]:

    if current_folder.name.lower().strip() in ignore_list_local:
        console.rule(f'[yellow]Ignoring folder {current_folder.name}')
        return current_folder

    console.rule(f'[blue]{current_folder.name}')
    print(f'[green]link: {current_folder.onshape_link}')
    print(f'[green]local: {current_folder.local_path}')
    print(f'[green]remote: {current_folder.remote_path}')


    try:
        dirs, files = listdir(current_folder.local_path)
    except FileNotFoundError:
        raise TraverseException(current_folder, f'folder "{current_folder.local_path}" not found')
    except:
        return current_folder

    current_remote_path = '/'.join(onshape.get_current_path_folders())
    if current_remote_path == '':
        os.system('notify-send "Maybe an Error" "Could not find current remote path" -u critical')
        input('press Enter when page finish loads')
        current_remote_path = '/'.join(onshape.get_current_path_folders())

    if isinstance(current_folder.parent, Folder):

        if current_folder.parent.remote_path != current_remote_path:
            print(f'[yellow]out of sync in "{current_remote_path}".   trying to recover')
            print(f'[yellow]current_path: {current_remote_path}')
            print(f'[yellow]parent path: {current_folder.parent.remote_path}')

            a_diff, b_diff = intersect(current_remote_path.split('/'), current_folder.parent.remote_path.split('/'))

            for _ in a_diff:
                driver.back()
            sleep(2)

            onshape.go_to_path(b_diff)

            current_remote_path = '/'.join(onshape.get_current_path_folders())

            if current_folder.parent.remote_path != current_remote_path:
                raise TraverseException(current_folder, f'out of sync in {current_remote_path}')
            print(f'[green]recovered "{current_remote_path}"')

            sleep(2)

    folder_els, files_els = onshape.find_files()
    for el in folder_els:
        if el.text.strip() == current_folder.name:
            onshape.act.click(el)
            sleep(2)
            break
    else:
        raise TraverseException(current_folder, f'Could not find "{current_folder.name}" element in onshape')

    current_folder.files = [
        File(
            file,
            remote_path=f'{current_folder.remote_path}/{file}',
            local_path=f'{current_folder.local_path}/{file}',
        )
        for file in files
    ]

    for file in current_folder.files:
        print(file.name)

    folder_els, files_els = onshape.find_files()

    transfer_files(
        onshape,
        dirs,
        files,
        [el.text.strip() for el in folder_els],
        [el.text.strip() for el in files_els],
        root=current_folder.local_path
    )


    for d in dirs:

        try:
            folder = traverse_local(
                google_drive,
                onshape,
                Folder(
                    d,
                    folders=[],
                    files=[],
                    remote_path=f'{current_folder.remote_path}/{d}',
                    local_path=f'{current_folder.local_path}/{d}',
                    parent=current_folder,
                    onshape_link=driver.current_url
                ),
                ignore_list_local
            )
        except KeyboardInterrupt:
            raise TraverseException(current_folder, 'Keyboard Interrupt')

        if not isinstance(folder, Folder):
            raise TraverseException(current_folder, 'Cannot put Root in a folder')

        current_folder.folders.append(folder)

            
    onshape.focus()
    onshape.driver.back()
    sleep(1)
    return current_folder

def traverse_drive(google_drive: GoogleDrive, onshape: Onshape, ignore_list:List[str]=[], ignore_list_local:List[str]=[]):
    google_drive.focus()
    sleep(0.5)

    file_history = Root(name='root', folders=[], files=[], remote_path='ThunderCatálogo', local_path=downloads_folder) 

    console.rule(f'[red]GOOGLE DRIVE')


    drive_folders = google_drive.find_files('folders')

    folders = [Folder(
                el.text,
                folders=[],
                files=[],
                remote_path=f'{file_history.remote_path}/{el.text}',
                local_path=f'{file_history.local_path}/{el.text}',
                parent=file_history,
                onshape_link=onshape.root_link
               ) for el in drive_folders]

    file_history.folders = folders

    # folder_els, _ = onshape.find_files()

    # transfer_files(
    #     [e.name for e in folders],
    #     [],
    #     [el.text.strip() for el in folder_els],
    #     [],
    #     root=downloads_folder
    # )

    for folder in folders:
        if folder.name.lower().strip() in ignore_list:
            console.rule(f'[red]Ignoring folder {folder.name}')
            continue

        try:
            # clear_downloads()
            google_drive.download_folder(folder)

            result = traverse_local(google_drive,onshape, folder, ignore_list_local)
        except TraverseException as e:
            os.system('notify-send "TraverseException" ":(" -u critical')
            print(f'[red]TraverseException: {e.message}')
            out_folder = copy(e.folder)
            out_folder.parent = None
            out_folder.folders = []
            print(out_folder)
            break
        except Exception as e:
            os.system('notify-send "Error" ":(" -u critical')
            print(f'[red]Error: {traceback.format_exc()}')
            break

        folder.folders = result.folders
        folder.files = result.files

    def dict_factory(x):
        exclude_fields = ("parent", )

        if is_dataclass(x):
            return {k: dict_factory(v) for (k, v) in x.__dict__.items() if ((v is not None) and (k not in exclude_fields))}
        elif isinstance(x, list):
            return [dict_factory(v) for v in x]

        return x

    try:
        file_history_dict = dict_factory(file_history)
    except RecursionError:
        print('[red]Recursion error')
        return

    with open(log_file, 'w') as f:
        print(f'[green]Saving log to "{log_file}"')
        json.dump(file_history_dict, f, indent=4)

    return file_history
