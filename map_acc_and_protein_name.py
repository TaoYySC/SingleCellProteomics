from concurrent.futures import ThreadPoolExecutor

import requests
import pandas as pd
from babel.messages.extract import extract

def extract_index_from_data():
    data = pd.read_csv('all_data_filtered.csv', index_col=0)
    index = data.index
    index = pd.DataFrame(index)
    index.to_csv('index.csv')


def get_protein_name(protein_id):
    # UniProt API URL，用Accession ID获取蛋白质信息
    url = f"https://www.uniprot.org/uniprot/{protein_id}.txt"

    try:
        response = requests.get(url)

        if response.status_code == 200:
            # 解析返回的文本数据
            protein_info = response.text.splitlines()
            protein_name = None

            # 遍历文本行，查找包含蛋白质名称的行（DE行）
            for line in protein_info:
                if line.startswith("DE   RecName: Full="):
                    protein_name = line.split('=')[1].strip()
                    break

            if protein_name:
                print(f"Protein Name: {protein_name}")
            else:
                print(f"Protein name not found for {protein_id}.")
        else:
            print(f"Error: Unable to retrieve data for {protein_id}. Status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def get_protein_id_from_name(protein_name):
    # UniProt 搜索API URL，用于查询蛋白质名称
    search_url = f"https://www.uniprot.org/uniprot/?query={protein_name}&format=txt"

    try:
        response = requests.get(search_url)

        if response.status_code == 200:
            # 返回的文本数据
            lines = response.text.splitlines()

            # 查找包含蛋白质Accession ID的行（通常以"AC   "开始）
            accession_id = None
            for line in lines:
                if line.startswith("AC   "):
                    accession_id = line.split()[1]  # 提取第一个Accession ID
                    break

            if accession_id:
                print(f"Accession ID for {protein_name}: {accession_id}")
                # 通过Accession ID获取蛋白质名称
                get_protein_name(accession_id)
            else:
                print(f"Accession ID for {protein_name} not found.")
        else:
            print(f"Error: Unable to retrieve data for {protein_name}. Status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")


def query_uniprot(query):
    url = "https://rest.uniprot.org/uniprotkb/search"
    headers = {"Accept": "application/json"}
    query_type = f"accession:{query}" if query.isalnum() and query[0].isupper() and len(
        query) >= 6 else f"protein_name:{query}"

    params = {
        "query": query_type,
        "fields": "accession,id",
        "format": "json"
    }

    try:
        print(query_type)
        response = requests.get(url, headers=headers, params=params, timeout=10)
        print(response.text)
        response.raise_for_status()
        data = response.json()
        print(f"query:{query}\n{data}")
        if "results" in data and len(data["results"]) > 0:
            result = data["results"][0]
            accession = result.get("primaryAccession", "Not Found")
            protein_name = result.get("uniProtkbId", "Not Found")
            return f"{accession} · {protein_name}"
    except Exception as e:
        return f"Error: {str(e)}"

    return "Not Found"

if __name__ == '__main__':
    protein_name = pd.read_csv('index.csv')
    list = protein_name.loc[:59]
    query = '1433B_HUMAN'
    result = get_protein_id_from_name(query)
    print(result)
    # for query in list:
    #     result = query_uniprot(query)
    #     list['Protein ID and Name'] = result
    #     print(result)
    # list.to_csv('result.csv')
