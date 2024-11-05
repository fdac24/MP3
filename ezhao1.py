import json, re
import requests
from urlextract import URLExtract
import sys, gzip


utid = 'ezhao1'
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

def extractBibEntries(content):
   res = re.findall(bib_pattern, content, re.DOTALL)
   return res

fo = gzip.open(f"output/{utid}.json.gz", 'w')

def run (tp):
   post0 = post
   with open(f"input/{utid}_{tp}", 'r') as f:
      for line in f:
         line = line.strip ()
         #it constructs it using postGH so git rid of .git postfix
         if line.endswith('.git'):
                line = line[:-4]
         if tp == 'source':
            (npapers,line) = line.split(';')
            post0 = postGH
         print(line)
         url = base[tp] + f"{line}{post0}"
         r = requests.get (url)

         if r.status_code == 404: #not found
            #try master
            if tp != 'source': continue
            
            post0 = '/blob/main/README.md'
            url = base[tp] + f"{line}{post0}"
            r = requests.get(url)

            #still not found so doesnt exist
            if r.status_code == 404:
               print(f"Repository '{line}' does not exist.")
               continue

         content = r.text
         urls = extractURLs(content)
         dois = extractDOIs(content)
         bibs = extractBibEntries(content)
         res = { 'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois, 'bibs': bibs}
         out = json.dumps(res, ensure_ascii=False)
         fo.write((out+"\n").encode())

run('model')
run('data')
run('source')