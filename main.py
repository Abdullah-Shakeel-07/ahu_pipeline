from crawl import process_keyword, get_response, capsolver_sdk, log_error, CacheManager
from db_insert import run as run_db
import string
import csv
import os
import pandas as pd


ERROR_FILE = 'error.csv'
ALPHABET = string.ascii_lowercase  # a-z
MIN_LENGTH = 3
OUTPUT_FILE = 'companie_data.csv'
FIELDNAMES = ["nbrs_id", "company_name", "company_type", "phone", "address", "kabpro", "source_file"]



def dfs(prefix, token=None):

    if len(prefix) > 3:
        return token

    cache_manager = CacheManager(base_path='ahu_cache')
    cache_key = f"{prefix}_1"

    if not cache_manager.get(cache_key):
        if not token:
            token = capsolver_sdk()

    response = get_response(page=1, nama=prefix, token=token)

    if not response:
        log_error(keyword=prefix, page=1)
        return token

    if "Pencarian Tidak Ditemukan" in response:
        print(f"dfs: no results for '{prefix}'. pruning branch.")
        return token

    process_keyword(prefix, token)

    # for char in ALPHABET:
    #     child = prefix + char
    #     token = dfs(child, token)  # reuse same token across children

    if len(prefix) < 4:
        for char in ALPHABET:
            child = prefix + char
            token = dfs(child, token)

    return token

def process_keyword_list(keywords, token=None):

    for keyword in keywords:

        # response = get_response(page=1, nama=keyword, token=token)

        # if not response:
        #     log_error(keyword=keyword, page=1)
        #     continue

        # if "Pencarian Tidak Ditemukan" in response:
        #     continue

        companies = process_keyword(keyword, token)
        save_companies(companies)

def generate_seeds():
    # 3 letter combinations as starting string like aaa, aab 
    for a in ALPHABET:
        for b in ALPHABET:
            for c in ALPHABET:
                yield f"{a}{b}{c}"

def save_companies(companies):
    
    if not companies:
        return
    file_exists = os.path.exists(OUTPUT_FILE)
    with open(OUTPUT_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerows(companies)



def main():
    # delete the output file if it exists becasue we are appending the output to the file
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    innput_file_name = "random_keywords.csv"

    USE_DFS = False

    if USE_DFS:
        for seed in generate_seeds():
            dfs(seed)

    else:
        KEYWORD_LIST = []

        with open(innput_file_name, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                KEYWORD_LIST.append(row["keywords"])

        process_keyword_list(KEYWORD_LIST)

    # loading the file, removing the duplicated and uncessary column (i used them for testing the data)
    df = pd.read_csv(OUTPUT_FILE, dtype = str)

    df = df[['nbrs_id', 'company_name', 'company_type', 'phone', 'address']]

    df.drop_duplicates(inplace = True)

    df.to_csv(OUTPUT_FILE, index = False)

    print("writing data to dbb")
    run_db(input_csv=OUTPUT_FILE)


if __name__ == "__main__":
    main()
