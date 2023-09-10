from rich import print
import json
import os

merged_log = {}
with open('merged_log.json') as f:
    merged_log = json.load(f)


def parse(source):
    files = {}
    folders = {}

    for item in source.get('files', []):
        files[item['name']] = parse(item)
        del item['name']

    for item in source.get('folders', []):
        folders[item['name']] = parse(item)
        del item['name']

    source['files'] = files
    source['folders'] = folders


    return source


parsed_log = parse(merged_log)

os.makedirs('logs', exist_ok=True)
with open('logs/parsed_log.json', 'w') as f:
    json.dump(parsed_log, f, indent=2)

# print(parse(merged_log))

