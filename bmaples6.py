# Brent Maples - bmaples6
# November 4th, 2024
# CS445 - MP3
import json, re
import requests
from urlextract import URLExtract
import sys, gzip


utid = 'bmaples6'
base= { 'model':'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://' }
post = '/raw/main/README.md'
postGH = 'blob/master/README.md' # or it could be 'blob/main/README.md'

extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'
#r1\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])[[:graph:]])+)\b'
BIBpattern = r'@(\w+)\{([^,]+),\s*((?:.|\n)*?)\n\}\n'
def extractURLs (c):
 res = extU.find_urls (c)
 return res

def extractDOIs (c):
 res = re.findall (DOIpattern, c)
 return res

def extractBIBs (c):
   res = re.findall(BIBpattern, c, re.DOTALL)
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
   if r.status_code != 200:
      if tp != 'source': continue
      else:
         #Trying 'blob/main/README.md' instead of 'blob/master/README.md'
         alt_url = url.replace('blob/master', 'blob/main')
         r = requests.get(alt_url)
         if r.status_code != 200: continue
         else: url = alt_url
      
   content = r.text;
   #github returns repos that do not exist, need to detect that here
   #github when you give master instead of main, that might cause issues as well
   urls = extractURLs(content)
   dois = extractDOIs(content)
   bibs = extractBIBs(content)
   res = { 'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois, 'bibs': bibs}
   out = json.dumps(res, ensure_ascii=False)
   fo.write((out+"\n").encode())

run('model')
run('data')
run('source')