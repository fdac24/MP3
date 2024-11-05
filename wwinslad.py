import json, re
import requests
from urlextract import URLExtract
import sys, gzip


utid = 'wwinslad'
base= { 'model':'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://' }
post = '/raw/main/README.md'
postGH = 'blob/master/README.md' 
# In my testing, GitHub automatically redirects to main if master doesn't exist and displays README.md anyway

extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'
#r1\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])[[:graph:]])+)\b'

def extractURLs (c):
 res = extU.find_urls (c)
 return res

def extractDOIs (c):
 res = re.findall (DOIpattern, c)
 return res

# Kind of finnicky since regex doesn't like nested braces, but works good enough for most cases
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
   r = requests.get (url)
   content = r.text

   #github returns repos that do not exist, need to detect that here
   if 'This is not the web page you are looking for' in content:
    # This means the repo doesn't exist
    print(' --> Invalid repo: 404 error on repo path')
    res = { 'ID': line, 'type': tp, 'url': url, 'content': 'Invalid repo: 404 error on repo path', 'links': [], 'dois': [], 'bibs': [] }
   elif 'File not found' in content:
    # This means the repo exists but doesn't have a README.md file
    print(' --> Invalid file: 404 error on file path')
    res = { 'ID': line, 'type': tp, 'url': url, 'content': 'Invalid file: 404 error on file path', 'links': [], 'dois': [], 'bibs': [] }
   else:    
    # Can proceed normally
    urls = extractURLs(content)
    dois = extractDOIs(content)
    bibs = extractBibs(content)
    res = { 'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois, 'bibs': bibs }
   
   # Note: I found in my testing that GitHub automatically redirects to default branch if you try and navigate to one that doesn't exist
   # so there was no need for separate logic for "/blob/master/README.md" vs "/blob/main/README.md"

   out = json.dumps(res, ensure_ascii=False)
   fo.write((out+"\n").encode())

run('model')
run('data')
run('source')

fo.close()