import json, re
import requests
from urlextract import URLExtract
import sys, gzip


utid = 'dhodge12'
base= { 'model':'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://' }
post = '/raw/main/README.md'
postGH = 'blob/master/README.md' # or it could be 'blob/main/README.md'
postGHAlternate = 'blob/main/README.md'

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
 with open(f"input/{utid}_{tp}", 'r') as f:
  for line in f:
   line = line.strip ()
   if tp == 'source':
    (npapers,line) = line.split(';');
    post0 = postGH
   print(line)
   url = base[tp] + f"{line}{post0}"
   r = requests.get (url)

   # repo exist?
   if r.status_code == 404:
      # ensure we are looking at the source as the error
      if tp != 'source':
         continue
      
      # replace master with main
      url = base[tp] + f"{line}{postGHAlternate}"
      r = requests.get(url)

      # normal error 
      if r.status_code == 404:
        continue
         
   content = r.text;
   urls = extractURLs(content)
   dois = extractDOIs(content)
   res = { 'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois }
   out = json.dumps(res, ensure_ascii=False)
   fo.write((out+"\n").encode())

run('model')
run('data')
run('source')