import time
import requests
import capsolver
import os
import csv
from lxml import html
from dotenv import load_dotenv
from cache import CacheManager
from parse_data import parse_companies

load_dotenv()

# clearing proxy env vars(my vpn set this)
for var in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]:
    os.environ.pop(var, None)

VPN_PROXY = os.getenv("VPN_PROXY") 


def capsolver_sdk():
    print("solving captcha...")
    capsolver.api_key = os.getenv("CAPSOLVER_API_KEY")

    solution = capsolver.solve({
                "type": os.getenv("CAPTCHA_TYPE"),
                "websiteURL": "https://ahu.go.id/pencarian/profil-pt",
                "websiteKey": os.getenv("WEBSITE_KEY"),
              })

    token = solution.get('gRecaptchaResponse')
    return token



def make_request(page = 1, nama = None, token = None):


    cookies = {
        '___utmvm': '###########',
        'PHPSESSID': 'r9sd0kuud2m8k5s2evtrgadll2',
        '_ga': 'GA1.3.621138122.1774694808',
        '_ga_QQPNS0R6S7': 'GS2.3.s1774694810$o1$g0$t1774694810$j60$l0$h0',
        'TBMCookie_13113843438926760341': '489112001774846355vegms5VfvBS5LAO4bruQMZwGpUQ=',
        '___utmvc': "navigator%3Dtrue,navigator.vendor%3DGoogle%20Inc.,navigator.appName%3DNetscape,navigator.plugins.length%3D%3D0%3Dfalse,navigator.platform%3DWin32,navigator.webdriver%3Dfalse,plugin_ext%3Dno%20extention,ActiveXObject%3Dfalse,webkitURL%3Dtrue,_phantom%3Dfalse,callPhantom%3Dfalse,chrome%3Dtrue,yandex%3Dfalse,opera%3Dfalse,opr%3Dfalse,safari%3Dfalse,awesomium%3Dfalse,puffinDevice%3Dfalse,__nightmare%3Dfalse,domAutomation%3Dfalse,domAutomationController%3Dfalse,_Selenium_IDE_Recorder%3Dfalse,document.__webdriver_script_fn%3Dfalse,document.%24cdc_asdjflasutopfhvcZLmcfl_%3Dfalse,process.version%3Dfalse,navigator.cpuClass%3Dfalse,navigator.oscpu%3Dfalse,navigator.connection%3Dtrue,navigator.language%3D%3D'C'%3Dfalse,window.outerWidth%3D%3D0%3Dtrue,window.outerHeight%3D%3D0%3Dtrue,window.WebGLRenderingContext%3Dtrue,document.documentMode%3Dundefined,eval.toString().length%3D33,digest=",
    }

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Referer': 'https://ahu.go.id/pencarian/profil-pt',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        # 'Cookie': "___utmvm=###########; PHPSESSID=r9sd0kuud2m8k5s2evtrgadll2; _ga=GA1.3.621138122.1774694808; _ga_QQPNS0R6S7=GS2.3.s1774694810$o1$g0$t1774694810$j60$l0$h0; TBMCookie_13113843438926760341=489112001774846355vegms5VfvBS5LAO4bruQMZwGpUQ=; ___utmvc=navigator%3Dtrue,navigator.vendor%3DGoogle%20Inc.,navigator.appName%3DNetscape,navigator.plugins.length%3D%3D0%3Dfalse,navigator.platform%3DWin32,navigator.webdriver%3Dfalse,plugin_ext%3Dno%20extention,ActiveXObject%3Dfalse,webkitURL%3Dtrue,_phantom%3Dfalse,callPhantom%3Dfalse,chrome%3Dtrue,yandex%3Dfalse,opera%3Dfalse,opr%3Dfalse,safari%3Dfalse,awesomium%3Dfalse,puffinDevice%3Dfalse,__nightmare%3Dfalse,domAutomation%3Dfalse,domAutomationController%3Dfalse,_Selenium_IDE_Recorder%3Dfalse,document.__webdriver_script_fn%3Dfalse,document.%24cdc_asdjflasutopfhvcZLmcfl_%3Dfalse,process.version%3Dfalse,navigator.cpuClass%3Dfalse,navigator.oscpu%3Dfalse,navigator.connection%3Dtrue,navigator.language%3D%3D'C'%3Dfalse,window.outerWidth%3D%3D0%3Dtrue,window.outerHeight%3D%3D0%3Dtrue,window.WebGLRenderingContext%3Dtrue,document.documentMode%3Dundefined,eval.toString().length%3D33,digest=",
    }

    params = {
        'recaptcha-version': '3',
        'g-recaptcha-response': token,
        'tipe': 'perseroan',
        'nama': nama,
        'page': str(page),
    }

    response = requests.get(
        'https://ahu.go.id/pencarian/profil-pt/',
        params=params,
        cookies=cookies,
        headers=headers,
        proxies={"http": VPN_PROXY, "https": VPN_PROXY} if VPN_PROXY else None
    )

    return response

def proceed_further(response_text):
    if "Pencarian Tidak Ditemukan" in response_text: # it mean no result found
        return False
    else:
        return True

def get_response(page=1, nama=None, token=None):
    cache_manager = CacheManager(base_path='ahu_cache')
    cache_key = f"{nama}_{page}"
    print(f"cache key: {cache_key}")

    if cache_manager.get(cache_key):
        print(f"cache hit")
        return cache_manager.get_data(cache_key)

    print(f"cache miss. making request")
    if not token:
        token = capsolver_sdk()

    MAX_RETRIES = 3

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"attempt{attempt}/{MAX_RETRIES}")

        # making request and reuse the same token if fails
        try:
            response = make_request(page, nama, token)
        except Exception as exc:
            print(f"exception on attempt {attempt}: {exc}. retrying with same token")
            continue

        # status != 200 then reuse the same token and retry
        if response.status_code != 200:
            print(f"status: ({response.status_code}) on attempt {attempt}. retrying with same token")
            continue

        response_text = response.text

        # captcha expired, now resolve it
        if "Terjadi kesalahan ketika memvalidasi reCAPTCHA, silakan coba lagi." in response_text:
            print(f"captcha expired on attempt {attempt}. resolving...")
            time.sleep(2)
            token = capsolver_sdk()
            continue

        # # valid response, save to cache and return
        # if "Pencarian Tidak Ditemukan" in response_text: # it mean no result found
        #     print(f"no results found.")
        #     cache_manager.save(cache_key, response_text)
        #     return "End"

        cache_manager.save(cache_key, response_text)
        return response_text

    return None

def pagination(response_text):
    tree = html.fromstring(response_text)

    # get all pages 
    pages = tree.cssselect('a.search-pagination')
    if not pages:
        return 1
    
    # last page numnber = total number of pages
    total_pages = int(float(pages[-1].text_content().strip()))
    return total_pages
    
def log_error(keyword, page=1):

    file_exists = os.path.exists('error.csv')
    with open('error.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['keyword', 'page'])
        if not file_exists:
            writer.writeheader()
        writer.writerow({'keyword': keyword, 'page': page})

def process_keyword(nama, token=None):
    all_companies = []

    response = get_response(page=1, nama=nama, token=token)
    if not response:
        return []

    if not proceed_further(response):
        return []

    # parse page 1
    source_file = f"{nama}_1.html"
    all_companies.extend(parse_companies(response, source_file))
    # return all_companies

    total_pages = pagination(response)
    print(f"total pages: {total_pages}")

    if total_pages > 5: # for some keywords the total pages are invalid even on UI e.g: aba, abb, agn, ape, bad, baj
        total_pages = 2

    for page in range(2, total_pages + 1):
        print(f"page {page}/{total_pages}")
        response = get_response(page=page, nama=nama, token=token)
        if not response:
            print(f"error on page {page}")
            log_error(keyword=nama, page=page)
            continue
        if not proceed_further(response):
            print("no further results")
            break

        # parse each page
        source_file = f"{nama}_{page}.html"
        all_companies.extend(parse_companies(response, source_file))

    return all_companies


# process_keyword("aaa")