import requests
from bs4 import BeautifulSoup
from ast import literal_eval
from pathlib import Path

resource_file_path = Path('cache.json')
resource_file_path.touch(exist_ok=True)
resource_file = open(resource_file_path, 'r')
resources = resource_file.read()

if resources == '':
    trunk = {'name':'trunk',
        'url':'https://tn211.myresourcedirectory.com/index.php/component/cpx/?task=services.tree&amp;Itemid=107',
        'children':[]}
else:
    trunk = literal_eval(resources.replace('\n', ''))

# Recursively crawl lists of categories until it reaches a link to resources
def get_category_links(obj):
    if 'children' in obj.keys():
        if obj['children']!=[]:
            for item in obj['children']:
                get_category_links(item)
        else:
            print("\nGetting", obj['url'])
            page = requests.get(obj['url'], timeout=20)
            status = page.status_code
            print("Recieved with status", status)

            page_content = BeautifulSoup(page.content, 'html.parser')
            last_page = page_content.find('p', {'id': 'providers-found'})

            if (last_page is None): # keep iterating in category
                category_container = page_content.find('div', {'id': 'tree-view'})
                category_names = category_container.find_all('p', {'class': 'service-name'})

                # Make list of sub-categories from the page
                category_links = [{'name':a.find('a').text,
                    'url':'https://tn211.myresourcedirectory.com'+a.find('a', href=True)['href'],
                    'children':[]} for a in category_names]

                obj['children']=category_links
                for link in category_links:
                    get_category_links(link)

            else: # Once at page pointing to resources, call function to scrape resource list
                link='https://tn211.myresourcedirectory.com'+last_page.find('a', href=True)['href']
                get_resource_links(link, obj)

def get_resource_links(url, obj):
    global trunk
    print("\nGetting", url)
    page = requests.get(url, timeout=20)
    status = page.status_code
    print("Recieved with status", status)

    page_content = BeautifulSoup(page.content, 'html.parser')
    rows = page_content.find_all('div', {'class': 'result-row'})

    page_resources=list()
    for row in rows:
        d={}
        d['category']=obj['name']
        if row.find('p', {'class': 'resource-name'}).find('a') is not None:
            d['name']=row.find('p', {'class': 'resource-name'}).find('a').text
        else:
            d['name']=''

        if row.find('p', {'class': 'resource-name'}).find('a', href=True) is not None:
            d['url']='https://tn211.myresourcedirectory.com'+row.find('p', {'class': 'resource-name'}).find('a', href=True)['href']
        else:
            d['url']=''

        if row.find('p', {'class': 'resource-description'}) is not None:
            d['description']=row.find('p', {'class': 'resource-description'}).text
        else:
            d['description']=''

        if row.find('p', {'class': 'services'}) is not None:
            d['services']=row.find('p', {'class': 'services'}).text
        else:
            d['services']=''

        if row.find('div', {'class': 'resource-address'}) is not None:
            d['address']=row.find('div', {'class': 'resource-address'}).text.replace('\n', '')
        else:
            d['address']=''

        page_resources.append(d)

    pagination = page_content.find_all('div', {'class': 'pagination'})

    if pagination==[]:
        obj['children']=obj['children']+page_resources
        resource_file = open(resource_file_path, 'w')
        resource_file.write(str(trunk))
        resource_file.close()
    else:
        next_button = pagination[-1].find_all('div')[-1]
        end_page='disabled' in next_button.attrs['class']

        if end_page:
            obj['children']=obj['children']+page_resources
            resource_file = open(resource_file_path, 'w')
            resource_file.write(str(trunk))
            resource_file.close()
        else:
            obj['children']=obj['children']+page_resources
            resource_file = open(resource_file_path, 'w')
            resource_file.write(str(trunk))
            resource_file.close()
            next_page = pagination[-1].find_all('a', href=True)[-1]['href']
            get_resource_links('https://tn211.myresourcedirectory.com'+next_page, obj)


### Actually start the process
get_category_links(trunk)
