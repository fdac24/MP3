import json, re
import requests
from urlextract import URLExtract
import sys, gzip

utid = 'amarlow6'
base = { 'model': 'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://' }
post_main = '/raw/main/README.md'
post_master = '/raw/master/README.md'  # Fallback to master branch for README
postGH_main = '/blob/main/README.md'
postGH_master = '/blob/master/README.md'

extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'  # Given
BIBpattern = r"([A-Z][a-z]+,?\s(?:[A-Z]\.\s?)*)\(?\d{4}\)?:?.*?(?:https?://)?(?:www\.)?github\.com/([\w-]+/[\w-]+)"  # From chatGPT


#functions for extraction, ignore case seemed to work better for me
def extractURLs(c):
    return extU.find_urls(c)

def extractDOIs(c):
    return re.findall(DOIpattern, c, re.IGNORECASE)

def extractBIBs(c):  # For extra points
    return re.findall(BIBpattern, c, re.IGNORECASE)

fo = gzip.open(f"output/{utid}.json.gz", 'w')

def run(tp):
    post0 = post_main
    postGH0 = postGH_main
    with open(f"input/{utid}_{tp}", 'r') as f: #iterate through specific folder
        for line in f:
            line = line.strip()
            if tp == 'source':
                (npapers, line) = line.split(';')  # Ignore # of references
                post0, postGH0 = postGH_main, postGH_master
            
            print(f"Processing URL ID: {line}")
            url = base[tp] + f"{line}{post0}"

            try:
                # First, try fetching from the main branch
                r = requests.get(url, timeout=5)
                
                # If main branch returns 404, attempt to fetch from master branch
                if r.status_code == 404:
                    print(f"Main branch not found for {url}. Trying master branch.")
                    post0 = post_master  # Update to master branch
                    url = base[tp] + f"{line}{post0}"
                    r = requests.get(url, timeout=5)
                
                # Check if page exists after both attempts
                if r.status_code != 200:
                    print(f"URL {url} not found ({r.status_code})")
                    continue  # Skip to next line if the page doesn't exist

                content = r.text

                # Run all extractors
                urls = extractURLs(content)
                dois = extractDOIs(content)
                bibs = extractBIBs(content)

                # Create dictionary
                res = { 'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois, 'bibs': bibs }  # As specified
                out = json.dumps(res, ensure_ascii=False)
                fo.write((out + "\n").encode())
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching {url}: {e}")

# Run for each type, limiting to the first item per category
run('model')
run('data')
run('source')

fo.close()
