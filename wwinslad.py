import json, re
import requests
from urlextract import URLExtract
import sys, gzip


utid = 'wwinslad'
base= { 'model':'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://' }
post = '/raw/main/README.md'
postGH = 'blob/master/README.md' # or it could be 'blob/main/README.md'
postGH_alt = 'blob/main/README.md'

extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'
#r1\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])[[:graph:]])+)\b'

def extractURLs (c):
 res = extU.find_urls (c)
 return res

def extractDOIs (c):
 res = re.findall (DOIpattern, c)
 return res

def extractBibs(c):
   BibtexPattern = r'@(\w+)\s*{\s*([^,]+),\s*([^}]*)}'
   res = re.findall (BibtexPattern, c)
   return res

fo = gzip.open(f"output/{utid}.json.gz", 'w')

def run (tp):
 post0 = post
 with open(f"input/{utid}_{tp}", 'r') as f:
  for line in f:
   line = line.strip ()
   if tp == 'source':
    (npapers,line) = line.split(';')
    post0 = postGH
   print(line)
   url = base[tp] + f"{line}{post0}"
   r = requests.get(url)
   content = r.text

   #github returns repos that do not exist, need to detect that here
   if 'Page not found' in content:
     print(f"Repo not found: {line}")
     res = { 'ID': line, 'type': tp, 'url': url, 'content': 'Repo not found', 'links': [], 'dois': [], 'bibs': [] }
     out = json.dumps(res, ensure_ascii=False)
     fo.write((out+"\n").encode())
     continue

   #github when you give master instead of main, that might cause issues as well
   if 'File not found' in content:
    print(f"404, switching to main: {line}")
    url = base[tp] + f"{line}{postGH_alt}"
    r = requests.get(url)
    content = r.text

   urls = extractURLs(content)
   dois = extractDOIs(content)
   bibs = extractBibs(content)
   res = { 'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois, 'bibs': bibs }
   out = json.dumps(res, ensure_ascii=False)
   fo.write((out+"\n").encode())

run('model')
run('data')
run('source')