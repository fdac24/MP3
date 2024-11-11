import json, re
import requests
from urlextract import URLExtract
import gzip
import time

utid = 'jkutbay'
base = {'model': 'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://'}
post_main_variants = ['/raw/main/README.md', '/raw/main/readme.md', '/raw/main/ReadMe.md']
post_master_variants = ['/blob/master/README.md', '/blob/master/readme.md', '/blob/master/ReadMe.md']

extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'

def extractURLs(c):
    res = extU.find_urls(c)
    return res

def extractDOIs(c):
    res = re.findall(DOIpattern, c)
    return res

fo = gzip.open(f"output/{utid}.json.gz", 'w')

def run(tp):
    with open(f"input/{utid}_{tp}", 'r') as f:
        for line in f:
            line = line.strip()
            if tp == 'source':
                (npapers, line) = line.split(';')
                post_variants = post_master_variants
            else:
                post_variants = post_main_variants

            print(line)
            content = None
            url = None

            for post in post_variants:
                url = base[tp] + f"{line}{post}"
                
                time.sleep(0.5) # prevent too many requests
                r = requests.get(url)
                if r.status_code == 200:
                    content = r.text
                    break

            if content is None:
                continue

            urls = extractURLs(content)
            dois = extractDOIs(content)

            res = {
                'ID': line,
                'type': tp,
                'url': url,
                'content': content.replace("\n", " "),
                'links': urls,
                'dois': dois
            }
            
            out = json.dumps(res, ensure_ascii=False)
            fo.write((out + "\n").encode())

run('model')
run('data')
run('source')
fo.close()
