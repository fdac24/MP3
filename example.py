import json, re
import requests
from urlextract import URLExtract
import sys, gzip


utid = 'edayney' # For output file

# Base URLs for different repository types
base= { 'model':'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://' }

# README paths for huggingface and github respectively
post = '/raw/main/README.md'
postGH = 'blob/master/README.md' # or it could be 'blob/main/README.md'

# Store URLExtract object for use in URL extraction functions
extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'
#r1\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])[[:graph:]])+)\b'

# Extracts all URLs in the content
def extractURLs (c):
 res = extU.find_urls (c)
 return res

# Extracts all Digital Object Identifiers in the content
def extractDOIs (c):
 res = re.findall (DOIpattern, c)
 return res

# Functional output? Sends output to json file
fo = gzip.open(f"output/{utid}.json.gz", 'w')

def run (tp):
 # Used to build the path to the README files
 post0 = post
 with open(f"input/{utid}_{tp}", 'r') as f:
  for line in f:
   line = line.strip ()
   if tp == 'source':
    (npapers,line) = line.split(';');
    post0 = postGH
   print(line)
   
   # Build out the URL to the README file
   url = base[tp] + f"{line}{post0}"
   r = requests.get (url)
   content = r.text
   
   #github returns repos that do not exist, need to detect that here
   #github when you give master instead of main, that might cause issues as well
   urls = extractURLs(content)
   dois = extractDOIs(content)
   res = { 'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois }
   out = json.dumps(res, ensure_ascii=False)
   fo.write((out+"\n").encode())

run('model')
print("FINISHED MODEL PORTION")
run('data')
print("FINISHED DATA PORTION")
run('source')
print("FINISHED SOURCE PORTION")