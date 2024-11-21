import json, re
import requests
from urlextract import URLExtract
import sys, gzip

utid = 'gpatel8'
base= { 'model':'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://' }
post = '/raw/main/README.md'
postGHM = '/blob/master/README.md' # or it could be 'blob/main/README.md'
postGHMain = '/blob/main/README.md'
url_extractor = URLExtract()
doi_pattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b'

def extractURLs (c):
   res = url_extractor.find_urls (c)
   return res

def extractDOIs (c):
   res = re.findall (doi_pattern, c)
   return res

fo = gzip.open(f"output/{utid}.json.gz", 'w')

def run (tp):
   post0 = post
   with open(f"input/{utid}_{tp}", 'r') as f:
      for line in f:
         line = line.strip ()
         if tp == 'source':
            (npapers,line) = line.split(';');
            post0 = postGHM
         print(line)
         url = base[tp] + f"{line}{post0}"
         r = requests.get(url)

         if r.status_code == 404 and tp == "source":
            url = base[tp] + f"{line}{postGHMain}"
            r = requests.get(url)

         if r.status_code == 404:
            continue
         
         content = r.text
         urls = extractURLs(content)
         dois = extractDOIs(content)

         res = { 'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois }
         out = json.dumps(res, ensure_ascii=False)
         fo.write((out+"\n").encode())

run('model')
run('data')
run('source')