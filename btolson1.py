import json, re
import requests
from urlextract import URLExtract
import sys, gzip
import bibtexparser

utid = 'btolson1'
base= { 'model':'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://' }
post = '/raw/main/README.md'
postGH = 'blob/master/README.md' # or it could be 'blob/main/README.md'

extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'
#r1\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])[[:graph:]])+)\b'
bib_pattern = r'@\w+\{[^}]+\}'

def extractURLs (c):
 res = extU.find_urls (c)
 return res

def extractDOIs (c):
 res = re.findall (DOIpattern, c)
 return res

# Tried to find a decent bib pattern for bib-text citations
def extractBibs (c):
 res = re.findall(bib_pattern, c)
 return res

fo = gzip.open(f"output/{utid}.json.gz", 'w')

def run (tp):
 post0 = post
 with open(f"input/{utid}_{tp}", 'r', encoding='utf-8') as f:
  for line in f:
   line = line.strip ()
   if tp == 'source':
    (npapers,line) = line.split(';');
    post0 = postGH
   print(line)
   url = base[tp] + f"{line}{post0}"
   r = requests.get (url)
   content = r.text;
   #github returns repos that do not exist, need to detect that here
   #github when you give master instead of main, that might cause issues as well
   urls = extractURLs(content)
   dois = extractDOIs(content)
   bib =  extractBibs(content)
   res = { 'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois, 'bibs': bib }
   out = json.dumps(res, ensure_ascii=False)
   fo.write((out+"\n").encode())

run('model')
run('data')
run('source')