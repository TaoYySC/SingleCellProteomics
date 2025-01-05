import requests
from bs4 import BeautifulSoup
import re


url = f'https://singpro.idrblab.net/'
response = requests.get(url)
# response = requests.get(url, proxies={})


html = response.text
soup = BeautifulSoup(html, 'html.parser')
target_div = soup.find('div', class_='search-title-name', string='Search for MS-based SCP by Tissue/Organ:')
form = target_div.find_next_sibling('form')
options = form.find_all('option')
tissues = [option.get_text() for option in options if option.get_text() != "Please select a tissue/organ"]

print(tissues)

for tissue in tissues:
    url = f"https://singpro.idrblab.net/search/result/ms-by-list?name={tissue}"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        print(f"Page for {tissue}:")
    else:
        print(f"Failed to retrieve page for {tissue}. Status code: {response.status_code}")
    project_ids = []
    for span in soup.find_all('span', class_='font-search'):
        text = span.get_text()
        if 'Project ID:' in text:
            project_id = text.split('Project ID: ')[1].strip()
            project_ids.append(project_id)
    print(project_ids)