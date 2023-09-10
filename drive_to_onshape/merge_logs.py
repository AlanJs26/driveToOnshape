import json
import os
from glob import glob
from typing import List, Tuple, TypedDict, NotRequired
from rich import print
from dataclasses import dataclass
from rich.console import Console

logs = sorted(glob('src/logs/log-*.json'))

class FolderType(TypedDict):
    name: str
    remote_path: str
    local_path: str
    onshape_link: str
    files: 'NotRequired[List[FolderType]]'
    folders: 'NotRequired[List[FolderType]]'

@dataclass
class PairsResult():
    pairs: List[Tuple[FolderType, FolderType]]
    source_unique: List[FolderType]
    destination_unique: List[FolderType]



def find_pairs(source: List[FolderType], destination: List[FolderType]) -> PairsResult:
    result = PairsResult(pairs= [], source_unique= [], destination_unique= [])

    dest_names = [el['name'] for el in destination]

    for dest in destination:
        for sour in source:
            if sour['name'] == dest['name']:
                result.pairs.append((sour, dest))
                break
        else:
            result.destination_unique.append(dest)

    for sour in source:
        if sour['name'] not in dest_names:
            result.source_unique.append(sour)

    return result

def merge(source, destination):
    merged:FolderType = {
        'name': destination.get('name') or source.get('name'),
        'remote_path': destination.get('remote_path') or source.get('remote_path') or '',
        'local_path': destination.get('local_path') or source.get('local_path') or '',
        'onshape_link': destination.get('onshape_link') or source.get('onshape_link') or '',
        'files': [],
        'folders': [],
    }

    if not merged['name']:
        return source

    pairs_result = find_pairs(source.get('files', []), destination.get('files', []))

    merged['files'] = [merge(s, d) for s, d in pairs_result.pairs]
    merged['files'].extend((
            *pairs_result.destination_unique,
            *pairs_result.source_unique
        ))

    pairs_result = find_pairs(source.get('folders', []), destination.get('folders', []))

    merged['folders'] = [merge(s, d) for s, d in pairs_result.pairs]
    merged['folders'].extend((
            *pairs_result.destination_unique,
            *pairs_result.source_unique
        ))
    # print(len(merged['folders']))

    return merged

merged_logs = {}

console = Console()

for log in logs[0:8]:
    console.rule(log)
    with open(log) as f:
        source = json.load(f)
        pairs_result = find_pairs(source.get('folders', []), merged_logs.get('folders', []))

        unique_pairs = list(filter(lambda e: len(e[0]['folders']) != len(e[1]['folders']), pairs_result.pairs))
        if unique_pairs:
            print(unique_pairs)


        merged_logs = merge(source, merged_logs)

os.makedirs('logs', exist_ok=True)
with open('logs/merged_log.json', 'w') as f:
    json.dump(merged_logs, f, indent=2)
print(merged_logs)

