import csv
import json
from operator import delitem
import requests
from bs4 import BeautifulSoup
from ast import Not, literal_eval
from pathlib import Path

resource_file_path = Path('cache.json')
resource_file_path.touch(exist_ok=True)

resource_file = open(resource_file_path, 'r')
resource_cache = resource_file.read()

if resource_cache == '':
    trunk = {'name': 'trunk',
             'url': 'https://tn211.myresourcedirectory.com/index.php/component/cpx/?task=services.tree&amp;Itemid=107',
             'children': []}
else:
    trunk = literal_eval(resource_cache.replace('\n', ''))


def get_resources_list(obj, resources = []):
    if 'children' in obj.keys() and obj['children'] != []:
        for item in obj['children']:
            if 'description' in item.keys():
                resources.append(item)
            resources = get_resources_list(item, resources)
    return resources

resources = get_resources_list(trunk)

writer = csv.DictWriter(
    open('resources.csv', 'w', encoding='UTF8', newline=''), 
    fieldnames=['name','description','address','category','services','link']
)

writer.writeheader()
writer.writerows(resources)