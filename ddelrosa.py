import json, re
import requests
from urlextract import URLExtract
import sys, gzip


utid = 'ddelrosa'
base= { 'model':'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://' }
post = '/raw/main/README.md'
postGH_master = 'blob/master/README.md' # or it could be 'blob/main/README.md'
postGH_main = 'blob/main/README.md'

extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'
#r1\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])[[:graph:]])+)\b'
BIBpattern = r'@.*?{.*?}' 
# BIBpattern = r'\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])[[:graph:]])+)\b'

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
    (npapers,line) = line.split(';')
    post0 = postGH_master
    post1 = postGH_main
   print(f"Doing stuff: {line}")
   url = base[tp] + f"{line}{post0}"
   r = requests.get (url)
   
#github returns repos that do not exist, need to detect that here
   if r.status_code != 200: 
      if tp != 'source':
         continue

      print (f"URL {url} error is {r.status_code} Trying again")
#github when you give master instead of main, that might cause issues as well
      url1 = base[tp] + f"{line}{post1}"
      r = requests.get (url1)
      if r.status_code != 200:
         print (f"Error still persiting for URL: {url1} error is {r.status_code}")
         continue
       
   content = r.text
   urls = extractURLs(content)
   dois = extractDOIs(content)
   bibs = extractBIBs(content)
   content = content.replace('\n', ' ')
   # bibs = bibs.replace('\n', ' ')
   res = { 'ID': line,
           'type': tp, 
           'url': url, 
           'content': content, 
           'links': urls, 
           'dois': dois,
           'bibs': bibs }
   out = json.dumps(res, ensure_ascii=False)
   fo.write((out+"\n").encode())

run('model')
run('data')
run('source')

fo.close()