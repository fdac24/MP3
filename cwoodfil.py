import json, re
import os
import requests
from urlextract import URLExtract
import sys, gzip

utid = 'cwoodfil'  
base= { 'model':'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://' }
post = '/raw/main/README.md'
postGH = 'blob/master/README.md'  

extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'

output_dir = 'output'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def extractURLs (c):
    res = extU.find_urls(c)
    return res

def extractDOIs (c):
    res = re.findall(DOIpattern, c)
    return res

fo = gzip.open(f"output/{utid}.json.gz", 'w')  

def run (tp):
    post0 = post
    with open(f"input/{utid}_{tp}", 'r') as f:  
        for line in f:
            line = line.strip()
            if tp == 'source':
                (npapers, line) = line.split(';')
                post0 = postGH
            print(line)
            url = base[tp] + f"{line}{post0}"
            r = requests.get(url)
            content = r.text
            # GitHub returns repos that do not exist, need to detect that here
            # GitHub when you give master instead of main, that might cause issues as well
            urls = extractURLs(content)
            dois = extractDOIs(content)
            res = { 'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois }
            out = json.dumps(res, ensure_ascii=False)
            fo.write((out + "\n").encode())

run('model')
run('data')
run('source')