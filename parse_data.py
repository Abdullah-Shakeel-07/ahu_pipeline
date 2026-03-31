import re
import unicodedata
from lxml import html
import os
import csv

COMPANY_TYPES = {
    'PT': 'Perseroan Terbatas',
    'CV': 'Commanditaire Vennootschap',
    'UD': 'Usaha Dagang',
    'FA': 'Firma',
    'TB': 'Toko Bangunan',
    'PD': 'Perusahaan Daerah',
    'PN': 'Perusahara Negara',
    'KOPERASI': 'Koperasi',
    'YAYASAN': 'Yayasan',
}

def normalize(text):
    if not text:
        return None
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_company_type(name):
    if not name:
        return 'Unknown'
    prefix = name.strip().split()[0].upper()
    return COMPANY_TYPES.get(prefix, 'Unknown')

def parse_companies(response_text, source_file):
    tree = html.fromstring(response_text)
    companies = []

    cards = tree.cssselect('div.cl0, div.cl1')

    for card in cards:
        nbrs_id  = card.cssselect('strong[data-id]')[0].get('data-id') if card.cssselect('strong[data-id]') else None
        raw_name = card.cssselect('strong.judul')[0].text_content() if card.cssselect('strong.judul') else None
        phone    = card.cssselect('div.telp')[0].text_content() if card.cssselect('div.telp') else None
        address  = card.cssselect('div.alamat')[0].text_content() if card.cssselect('div.alamat') else None
        kabpro   = card.cssselect('div.kabpro')[0].text_content() if card.cssselect('div.kabpro') else None

        clean_name = normalize(raw_name)

        companies.append({
            'nbrs_id':      nbrs_id,
            'company_name': clean_name,
            'company_type': extract_company_type(clean_name),
            'phone':        normalize(phone),
            'address':      normalize(address),
            'kabpro':       normalize(kabpro),
            'source_file':  source_file
        })

    return companies


if __name__ == "__main__":
    CACHE_DIR   = "./cache/ahu_cache"
    OUTPUT_FILE = "companies.csv"

    all_companies = []

    for file_name in os.listdir(CACHE_DIR):
        if not file_name.endswith(".html"):
            continue

        file_path = os.path.join(CACHE_DIR, file_name)

        with open(file_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        companies = parse_companies(html_content, file_name)
        all_companies.extend(companies)

    fieldnames = ["nbrs_id", "company_name", "company_type", "phone", "address", "kabpro", "source_file"]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_companies)
