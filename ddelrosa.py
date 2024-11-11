# Dylan DelRosa
# CS445
# MP3

import json, re
import requests
from urlextract import URLExtract
import sys, gzip


utid = 'ddelrosa'
base = { 'model':'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://' }
post = '/raw/main/README.md'
postGH_master = '/blob/master/README.md' # or it could be 'blob/main/README.md'
postGH_main = 'blob/main/README.md'

extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'
# BIBpattern : str = r'\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])[[:graph:]])+)\b'

BIBpattern: str = r'@.*?{.*?}'

def extractURLs (c):
 return extU.find_urls (c)

def extractDOIs (c):
 return re.findall (DOIpattern, c)

def extractBIBs (c):
  return re.findall (BIBpattern, c, re.DOTALL)

fo = gzip.open(f"output/{utid}.json.gz", 'w')

def run (tp):
 post0 = post
 post1 = post
 with open(f"input/{utid}_{tp}", 'r') as f:
  for line in f:
   line = line.strip ()
   if tp == 'source':
    (npapers,line) = line.split(';');
    post0 = postGH_master
    post1 = postGH_main
   print(line)
   url = base[tp] + f"{line}{post0}"
   r = requests.get (url)
# see if there is an error
   if r.status_code == 404:
      if tp != 'source':
         continue
# try and use 'blob/main/README.md' instead of 'blob/master/README.md'
      url1 = base[tp] + f"{line}{post1}"
      r = requests.get(url1)
# if still an error continue on
      if r.status_code == 404:
         continue
      
   content = r.text;
   urls = extractURLs(content)
   dois = extractDOIs(content)
   bibs = extractBIBs(content)
   res = { 'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois, 'bibs': bibs }
   out = json.dumps(res, ensure_ascii=False)
   fo.write((out+"\n").encode())

run('model')
run('data')
run('source')

fo.close()