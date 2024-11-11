import json
import re
import requests
from urlextract import URLExtract
import sys
import gzip


utid = 'dwang58'
base= { 'model':'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://' }
post = '/raw/main/README.md'
postGH = '/blob/master/README.md' # or it could be 'blob/main/README.md'

extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'
#r1\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])[[:graph:]])+)\b'
bib_pattern = r'@(\w+){[^}]+}'

def extractURLs (c):
   res = extU.find_urls (c)
   return res

def extractDOIs (c):
   res = re.findall (DOIpattern, c)
   return res

def extractBibs(c):
   res = re.findall(bib_pattern, c, re.DOTALL)
   return res

fo = gzip.open(f"output/{utid}.json.gz", 'w')

def run (tp):
   post0 = post
   with open(f"input/{utid}_{tp}", 'r') as f:
      for line in f:
         line = line.strip ()
         #deletes last four to get rid of .git
         if line.endswith('.git'):
                line = line[:-4]
         if tp == 'source':
            (npapers,line) = line.split(';')
            post0 = postGH
         print(line)
         url = base[tp] + f"{line}{post0}"
         r = requests.get (url)

         if r.status_code == 404:
            if tp != 'source': continue
            
            post0 = '/blob/main/README.md'
            url = base[tp] + f"{line}{post0}"
            r = requests.get(url)

            #Repository does not exist
            if r.status_code == 404:
               print(f"Repository '{line}' does not exist.")
               continue

         content = r.text
         urls = extractURLs(content)
         dois = extractDOIs(content)
         bibs = extractBibs(content)
         res = { 'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois, 'bibs': bibs}
         out = json.dumps(res, ensure_ascii=False)
         fo.write((out+"\n").encode())

run('model')
run('data')
run('source')
