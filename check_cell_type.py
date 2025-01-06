import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from util import get_tissues


def get_cell_type(SCP, path):
    url = f'https://singpro.idrblab.net/data/ms/details/{SCP}'
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    table = soup.find('table', class_='table-details')
    headers = [th.get_text(strip=True) for th in table.find('tr').find_all('td')]
    rows = []
    for tr in table.find('tbody').find_all('tr')[1:]:
        cells = [td.get_text(strip=True) for td in tr.find_all('td')]
        print(f"cells: {cells}")
        rows.append(cells)
    df = pd.DataFrame(rows, columns=headers)
    file_path = os.path.join(path,f'{SCP}','cell_info.csv')
    df.to_csv(file_path, index=False)

if __name__ == '__main__':
    main_url = f'https://singpro.idrblab.net/'
    study_type = "MS"
    tissues = get_tissues(main_url,study_type)
    for tissue in tissues:
        path = os.path.join('MS-based-SCP',tissue)
        print(f"path:{path}")
        scp_file_path = os.path.join(path,f'{tissue}.txt')
        with open(scp_file_path, 'r') as file:
            for line in file:
                line = line.strip()
                get_cell_type(line, path)