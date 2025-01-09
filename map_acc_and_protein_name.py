# from concurrent.futures import ThreadPoolExecutor
#
# import requests
# import pandas as pd
# from babel.messages.extract import extract
#
# def extract_index_from_data():
#     data = pd.read_csv('all_data_filtered.csv', index_col=0)
#     index = data.index
#     index = pd.DataFrame(index)
#     index.to_csv('index.csv')
#
#
# def query_uniprot(query):
#     """
#     查询 UniProt 数据，支持通过 Accession ID 或蛋白质名称获取结果。
#     返回格式为 "Accession · Protein Name"，如果未找到，则返回 "Not Found"。
#     """
#     url = "https://rest.uniprot.org/uniprotkb/search"
#     headers = {"Accept": "application/json"}
#
#     # 判断查询类型，自动适配 Accession ID 或蛋白质名称
#     query_type = f"accession:{query}" if query.isalnum() and query[0].isupper() and len(
#         query) >= 6 else f"protein_name:{query}"
#
#     params = {
#         "query": query_type,
#         "fields": "accession,id",
#         "format": "json"
#     }
#
#     try:
#         response = requests.get(url, headers=headers, params=params, timeout=10)
#         response.raise_for_status()
#         data = response.json()
#         if "results" in data and len(data["results"]) > 0:
#             result = data["results"][0]
#             accession = result.get("primaryAccession", "Not Found")
#             protein_name = result.get("uniProtkbId", "Not Found")
#             return f"{accession} · {protein_name}"
#     except Exception as e:
#         return f"Error: {str(e)}"
#
#     return "Not Found"
#
# if __name__ == '__main__':
#     # extract_index_from_data()
#     protein_name = pd.read_csv('index.csv')
#     list = protein_name.loc[:59]
#     # print(protein_name.loc[:59])
#     # query = protein_name['Protein IDs']
#     # print(query)
#     for query in list:
#         result = query_uniprot(query)
#         list['Protein ID and Name'] = result
#         print(result)
#     list.to_csv('result.csv')
#
#
import pandas as pd
import requests

# 查询函数
def query_uniprot(query):
    url = "https://rest.uniprot.org/uniprotkb/search"
    headers = {"Accept": "application/json"}
    query_type = f"accession:{query}" if query.isalnum() and query[0].isupper() and len(query) >= 6 else f"protein_name:{query}"
    params = {
        "query": query_type,
        "fields": "accession,id",
        "format": "json"
    }
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "results" in data and len(data["results"]) > 0:
            result = data["results"][0]
            accession = result.get("primaryAccession", "Not Found")
            protein_name = result.get("uniProtkbId", "Not Found")
            return f"{accession} · {protein_name}"
    except Exception as e:
        return f"Error: {str(e)}"
    return "Not Found"

# 加载数据
file_path = "index.csv"  # 替换为实际路径
df = pd.read_csv(file_path)

# 确保查询列有效
query_column = "Protein IDs"  # 替换为实际的查询列名
if query_column not in df.columns:
    raise ValueError(f"Column '{query_column}' not found in DataFrame")

# 去除空值或无效行
valid_queries = df[query_column].dropna()

# 新列名
result_column = "Protein ID and Name"

# 执行查询
df[result_column] = valid_queries.apply(query_uniprot)

# 保存结果
df.to_csv("output_with_protein_names.csv", index=False)
print("Processing complete. Results saved to 'output_with_protein_names.csv'.")
