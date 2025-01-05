import requests
from bs4 import BeautifulSoup
import os

def get_download_link(exp_num):
    exp_num = "SCP37621"

    url = f'https://singpro.idrblab.net/sites/files/file-ids/{exp_num}.txt'
    response = requests.get(url)
    # response = requests.get(url, proxies={})


    html = response.text

    soup = BeautifulSoup(html, 'html.parser')

    text = soup.get_text()

    file_path = f'{exp_num}.txt'
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(text)