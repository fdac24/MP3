import json, re
import requests
from urlextract import URLExtract
import sys, gzip


utid = 'snidiff1'
base= { 'model':'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://' }
post = '/raw/main/README.md'
postGH = '/raw/main/README.md' 
postGHalt = '/raw/master/README.md'

extU = URLExtract()
DOIpattern = r'\b10\.\d{4,9}/[-.;()/:\w]+'
#r1\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])[[:graph:]])+)\b'

def extractURLs (c):
 res = extU.find_urls (c)
 return res

def extractDOIs (c):
 res = re.findall (DOIpattern, c, re.IGNORECASE)
 return res

fo = gzip.open(f"output/{utid}.json.gz", 'w')

def run (tp):
 with open(f"input/{utid}_{tp}", 'r', errors='ignore') as f:
  for line in f:
   line = line.strip().partition('#')[0]
   if tp == 'source':
    (npapers,line) = line.split(';')
    post0 = postGHalt
   else:
    post0 = postGH
   print(line)

   url = base[tp] + f"{line}{post0}"
   print(url)

   try:
    r = requests.get (url)
    #github returns repos that do not exist, need to detect that here
    if r.status_code != 200:
     print("error, trying alt")
   
     #github when you give master instead of main, that might cause issues as well
     post0 = postGH if tp == 'source' else postGHalt
     url = base[tp] + f"{line}{post0}"
     print(url)
     r = requests.get (url)
     if r.status_code != 200:
      print("error code returned")
      continue
    
    content = r.text
    urls = extractURLs(content)
    dois = extractDOIs(content)
    res = { 'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois }
    out = json.dumps(res, ensure_ascii=False)
    fo.write((out+"\n").encode())

   except requests.exceptions.RequestException as e:
    print(f"Error fetching {url}: {e}")

run('model')
run('data')
run('source')

fo.close()