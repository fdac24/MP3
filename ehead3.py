import json, re
import requests
from urlextract import URLExtract
import gzip

utid = 'ehead3'
base = { 'model': 'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://' }
post_main = '/raw/main/README.md'
postGH = '/blob/master/README.md'

extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'
BIBpattern = r'@(\w+)\s*{\s*([^,]+),\s*([^}]*)}'  # BibTeX pattern

def extractURLs(content):
    return extU.find_urls(content)

def extractDOIs(content):
    return re.findall(DOIpattern, content, re.IGNORECASE)

def extractBIBs(content):
    return re.findall(BIBpattern, content)

fo = gzip.open(f"output/{utid}.json.gz", 'wt', encoding='utf-8')

def run(tp):
    post0 = post_main
    with open(f"input/{utid}_{tp}", 'r') as f:
        for line in f:
            line = line.strip()
            if tp == 'source':
                _, line = line.split(';', 1)
                post0 = postGH
            
            url = base[tp] + line + post0
            response = requests.get(url)
            content = response.text

            if 'This is not the web page you are looking for' in content or 'File not found' in content:
                print(f"Failed to retrieve {url}")
                res = {
                    'id': line,
                    'type': tp,
                    'url': url,
                    'content': 'Error: 404 or missing file',
                    'links': [],
                    'dois': [],
                    'bibs': []
                }
            else:
                urls = extractURLs(content)
                dois = extractDOIs(content)
                bibs = extractBIBs(content)
                res = {
                    'id': line,
                    'type': tp,
                    'url': url,
                    'content': content.replace('\n', ' '),
                    'links': urls,
                    'dois': dois,
                    'bibs': bibs
                }
            
            fo.write(json.dumps(res, ensure_ascii=False) + "\n")

run('model')
run('data')
run('source')
fo.close()