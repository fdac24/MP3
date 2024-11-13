# Alex Fowler   alecfowl
#MP3

import json, re
import requests
from urlextract import URLExtract
import sys, gzip


utid = 'alecfowl'
base= { 'model':'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://' }
post = '/raw/main/README.md'
postGH = 'blob/master/README.md' # or it could be 'blob/main/README.md'
postGH2 = 'blob/main/README.md'

extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'
#r1\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])[[:graph:]])+)\b'

def extractURLs (c):
   res = extU.find_urls (c)
   return res

def extractDOIs (c):
   res = re.findall (DOIpattern, c)
   return res

def extractBib (c):
   bibPattern = r'@(\w+)\{[^}]+\}'
   return re.findall(bibPattern, c)

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
            if tp != 'source':
               continue
            else:
               url2 = url.replace(postGH, postGH2)
               r = requests.get(url2)
               if r.status_code != 200:
                  continue
               else:
                  url = url2

         content = r.text
   #github returns repos that do not exist, need to detect that here
   #github when you give master instead of main, that might cause issues as well
         urls = extractURLs(content)
         dois = extractDOIs(content)
         bibs = extractBib(content)
         res = { 'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois, 'bibs': bibs }
         out = json.dumps(res, ensure_ascii=False)
         fo.write((out+"\n").encode())

run('model')
run('data')
run('source')