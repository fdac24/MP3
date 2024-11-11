import json
import re
import requests
import gzip
from urlextract import URLExtract

utid = 'jaugust4'
base = {'model': 'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://github.com/'}
post = '/raw/main/README.md'
postGH = 'blob/main/README.md'  # or it could be 'blob/main/README.md'
extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'

# Helper functions to extract URLs, DOIs, and Bib entries
def extractURLs(content):
    return extU.find_urls(content)

def extractDOIs(content):
    return re.findall(DOIpattern, content, re.IGNORECASE)

# Function to scrape README content and extract data
def scrape_readme(tp, file_name):
    post0 = post if tp != 'source' else postGH  # Adjust for GitHub source repos
    
    with open(f"input/{file_name}", 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if tp == 'source':
                (npapers, line) = line.split(';')
            url = base[tp] + f"{line}{post0}"
            print(f"Fetching {line}")
            try:
                response = requests.get(url)
                content = response.text
                urls = extractURLs(content)
                dois = extractDOIs(content)
                result = {
                    'id': line,
                    'type': tp,
                    'url': url,
                    'content': content,
                    'links': urls,
                    'dois': dois,
                }
                print(f"Printing {line}")
                fo = gzip.open(f"output/{utid}.json.gz", 'a')
                out = json.dumps(result, ensure_ascii=False)
                fo.write((out+'\n').encode('utf-8'))
            except requests.exceptions.RequestException as e:
                print(f"Failed to fetch {url}: {e}")
    return

# Execute the scraper
if __name__ == "__main__":
    all_results = []
    
    scrape_readme('model', f'{utid}_model')
    scrape_readme('data', f'{utid}_data')
    scrape_readme('source', f'{utid}_source')
