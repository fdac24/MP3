import json, re
import os
import requests
from urlextract import URLExtract
import sys, gzip

utid = 'mmccor23'
base = {
    'model': 'https://huggingface.co/', 
    'data': 'https://huggingface.co/datasets/', 
    'source': 'https://github.com/'
}
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

def extract_bibs(c):
    res = re.findall(r'@\w+\s*{[^}]+}', c)
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
            
            print(f"Grabbing - {line}")
            
            url = base[tp] + f"{line}{post0}"
            r = requests.get(url)
            
            # GitHub returns repos that do not exist, need to detect that here
            # GitHub when you give master instead of main, that might cause issues as well
            
            # Check if the URL returns a 404 error
            if r.status_code == 404 and tp == 'source':
            # Attempt to use 'main' instead of 'master' if the original URL fails
               url = url.replace('blob/master', 'blob/main')
               r = requests.get(url)

            if r.status_code == 404:
               print(f"Error - The repo at {url} does not exist or could not be found.")
               continue
      
            c = r.text
            urls = extractURLs(c)
            dois = extractDOIs(c)
            bibs = extract_bibs(c)
            result = {
                    'id': line,
                    'type': tp,
                    'url': url,
                    'content': c,
                    'links': urls,
                    'dois': dois,
                    'bibs': bibs
            }
            out = json.dumps(result, ensure_ascii=False)
            fo.write((out + "\n").encode())

run('model')
run('data')
run('source')