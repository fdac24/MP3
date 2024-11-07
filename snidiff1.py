import json, re
import requests
from urlextract import URLExtract
import sys, gzip


utid = 'snidiff1'
base= { 'model':'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://' }
post = '/raw/main/README.md'
postGH = '/blob/master/README.md' 
postGHalt = '/blob/main/README.md' # or it could be 'blob/main/README.md'

extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'
#r1\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])[[:graph:]])+)\b'

def extractURLs (c):
 res = extU.find_urls (c)
 return res

def extractDOIs (c):
 res = re.findall (DOIpattern, c)
 return res

fo = gzip.open(f"output/{utid}.json.gz", 'w')

def run (tp):
 post0 = post
 #put errors=ignore, was getting decoding errors
 with open(f"input/{utid}_{tp}", 'r', errors='ignore') as f:
  for line in f:
   line = line.strip ()
   if tp == 'source':
    (npapers,line) = line.split(';')
    post0 = postGH
   print(line)

   url = base[tp] + f"{line}{post0}"
   print(url)
   r = requests.get (url)
   #github returns repos that do not exist, need to detect that here
   #2xx status codes are sucesses, others are not
   if r.status_code < 200 or r.status_code > 299:
    print("error, trying main")
   
    #github when you give master instead of main, that might cause issues as well
    url = base[tp] + f"{line}{postGHalt}"
    print(url)
    r = requests.get (url)
    if r.status_code < 200 or r.status_code > 299:
     print("error code returned")
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

fo.close()