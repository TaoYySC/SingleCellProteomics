import os.path
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlsplit
import re

def get_next_page_url(soup):
    # Find the 'Next' page link by identifying the 'pager__item--next' class
    next_page_item = soup.find('li', class_='pager__item--next')
    if next_page_item:
        next_page_link = next_page_item.find('a', href=True)
        if next_page_link:
            return next_page_link['href']
    return None

def get_SCP_id(url,tissue, project_ids_dict, study_type):
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
    if tissue not in project_ids_dict:
        project_ids_dict[tissue] = []
    project_ids_dict[tissue].extend(project_ids)
    next_page_url = get_next_page_url(soup)
    if next_page_url:
        if study_type == "MS":
            next_page_url = f"https://singpro.idrblab.net/search/result/ms-by-list{next_page_url}"
        elif study_type == "FC":
            next_page_url = f"https://singpro.idrblab.net/search/result/ab-by-list{next_page_url}"
        get_SCP_id(next_page_url, tissue, project_ids_dict)

def get_tissues(url, study_type):
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    if study_type == "MS":
        target_div = soup.find('div', class_='search-title-name', string='Search for MS-based SCP by Tissue/Organ:')
    elif study_type == "FC":
        target_div = soup.find('div',class_='search-title-name', string='Search for FC-based SCP by Tissue/Organ:')
    else:
        print("wrong study type")
    form = target_div.find_next_sibling('form')
    options = form.find_all('option')
    tissues = [option.get_text() for option in options if option.get_text() != "Please select a tissue/organ"]
    print(tissues)
    return tissues

def get_download_link(tissue_folder,project_id):
    url = f'https://singpro.idrblab.net/sites/files/file-ids/{project_id}.txt'
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text()
    file_path = os.path.join(tissue_folder,f"{project_id}.txt")
    with open(file_path, 'w') as file:
        file.write(text)

def sava_project_id(tissue, project_ids, study_type):
    tissue_folder = os.path.join(f"{study_type}-based-SCP",tissue)
    if not os.path.exists(tissue_folder):
        os.makedirs(tissue_folder)
    file_path = os.path.join(tissue_folder,f"{tissue}.txt")

    with open(file_path, 'w') as file:
        for project_id in project_ids:
            get_download_link(tissue_folder,project_id)
            file.write(f"{project_id}\n")
def download_data(tissue, project_ids,study_type):
    for project_id in project_ids:
        project_id_path = os.path.join(f"{study_type}-based-SCP", tissue, f"{project_id}.txt")
        with open(project_id_path, 'r') as file:
            first_line = file.readline().strip()
            file_name, file_url = first_line.split('\t')
        response = requests.get(file_url)

        project_id_folder_path = os.path.join(f"{study_type}-based-SCP", tissue, project_id)
        if not os.path.exists(project_id_folder_path):
            os.makedirs(project_id_folder_path)
        data_name = os.path.basename(urlsplit(file_url).path)
        file_name = os.path.join(project_id_folder_path, data_name)
        if response.status_code == 200:
            with open(file_name, 'wb') as f:
                f.write(response.content)

def MS_download(url):
    study_type = "MS"
    tissues = get_tissues(url,study_type)
    project_ids_dict = {}
    for tissue in tissues:
        tissue_url = f"https://singpro.idrblab.net/search/result/ms-by-list?name={tissue}"
        get_SCP_id(tissue_url, tissue, project_ids_dict,study_type)
        print(project_ids_dict[tissue])
        sava_project_id(tissue, project_ids_dict[tissue],study_type)
        download_data(tissue, project_ids_dict[tissue],study_type)
        break
    return
def FC_download(url):
    study_type = "FC"
    tissues = get_tissues(url, study_type)
    project_ids_dict = {}
    for tissue in tissues:
        tissue_url = f"https://singpro.idrblab.net/search/result/ab-by-list?name={tissue}"
        get_SCP_id(tissue_url, tissue, project_ids_dict, study_type)
        print(project_ids_dict[tissue])
        sava_project_id(tissue, project_ids_dict[tissue], study_type)
        download_data(tissue, project_ids_dict[tissue], study_type)
        break
    return


if __name__ == '__main__':
    main_url = f'https://singpro.idrblab.net/'
    MS_download(main_url)

