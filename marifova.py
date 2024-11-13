import json, re
import requests
from urlextract import URLExtract
import sys, gzip

utid = 'marifova'
base = {'model': 'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://'}
post = '/raw/main/README.md'
postGH = '/blob/master/README.md'  # or it could be '/blob/main/README.md'

extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'
bibtex_pattern = r'@([a-zA-Z]+)\{([^,]+),([^}]+)\}'  # Basic BibTeX pattern

def extractURLs(c):
    """Extract URLs from the content."""
    return extU.find_urls(c)

def extractDOIs(c):
    """Extract DOIs from the content."""
    return re.findall(DOIpattern, c)

def extractBibs(c):
    """Extract BibTeX entries from the content using regex."""
    return re.findall(bibtex_pattern, c)

def fetch_content(url):
    """Fetch the content from the URL, handling GitHub repository issues (404, incorrect branch)."""
    try:
        r = requests.get(url)
        if r.status_code == 404:
            print(f"Error: Repository not found at {url}")
            return None  
        elif r.status_code != 200:
            print(f"Error: Failed to fetch {url}, Status code: {r.status_code}")
            return None  
        return r.text
    except requests.exceptions.RequestException as e:
        print(f"Request error while fetching {url}: {e}")
        return None  

fo = gzip.open(f"output/{utid}.json.gz", 'w')

def run(tp):
    post0 = post
    with open(f"input/{utid}_{tp}", 'r') as f:
        for line in f:
            line = line.strip()
            if tp == 'source':
                npapers, line = line.split(';')
                post0 = postGH

            print(f"Processing: {line}")
            url = base[tp] + f"{line}{post0}"
            content = fetch_content(url)
            
            if content is None:
                continue  

            if 'github.com' in url and 'master' not in post0 and 'main' in post0:
                print(f"Adjusting for 'master' branch instead of 'main' in URL: {url}")
                post0 = post0.replace('main', 'master') 

            urls = extractURLs(content)
            dois = extractDOIs(content)
            bibs = extractBibs(content) 

            # Format BibTeX entries
            formatted_bibs = [f"@{entry[0]}{{{entry[1]},{entry[2]}}}" for entry in bibs]

            res = {
                'ID': line,
                'type': tp,
                'url': url,
                'content': content,
                'links': urls,
                'dois': dois,
                'bibs': formatted_bibs 
            }
            out = json.dumps(res, ensure_ascii=False)
            fo.write((out + "\n").encode())

run('model')
run('data')
run('source')
