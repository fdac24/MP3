import json, re
import requests
from urlextract import URLExtract
import sys, gzip, os

utid = 'tcatunca'
base= { 'model':'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://raw.githubusercontent.com/' }
post = '/raw/main/README.md'
postGH = '/refs/heads/master/README.md' # or it could be 'ref/heads/main/README.md'

extU = URLExtract()
DOIpattern = r'10.\d{4,9}/[-._;()/:A-Z0-9]+'
BIBpattern = r'@[\w]+\{[^}]+\}'

def extractURLs (c):
   res = extU.find_urls (c)
   if res == []:
      return 'No URLs found'
   else:
      return res

def extractDOIs (c):
   res = re.findall (DOIpattern, c, re.IGNORECASE)
   if res == []:
      return 'No DOIs found'
   else:
      return res

def extractBIBs (c):
   res = re.findall(BIBpattern, c, re.IGNORECASE)
   if res == []:
      return 'No BIBs found'
   else:
      return res

fo = gzip.open(f"mp3/output/{utid}.json.gz", 'w')

def run(tp):
   contentCheck = ''
   
   with open(f"mp3/input/{utid}_{tp}", 'r') as f:
      for line in f:
         line = line.strip()
         if tp == 'source':
            (npapers, line) = line.split(';')
            line = line[11:]
         print(line)
         url = base[tp] + f"{line}{post}" if tp != 'source' else base[tp] + f"{line}{postGH}"
         r = requests.get(url)
         contentCheck = None

         if r.status_code == 404:
            if tp != 'source':
               print(f"-- URL not found, no README for: {url}")
               contentCheck = 'none'
            else:
               alternative_url = base[tp] + f"{line}{postGH.replace('master', 'main')}"
               r = requests.get(alternative_url)
                  
               if r.status_code == 404:
                  print("-- URL not found")
                  contentCheck = 'none'
               else:
                  url = alternative_url

         content = r.text.replace('\n', '')
         content = re.sub(r'\s+', ' ', content)
         content = content.replace('\\', "").replace('"', "\"").replace("'", "\'").replace('\t', ' ').replace('\r', ' ')
         if contentCheck == 'none':
            content = 'No content'
         urls = extractURLs(content)
         dois = extractDOIs(content)
         bibs = extractBIBs(content)
         res = {'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois, 'bibs' : bibs}
         out = json.dumps(res, ensure_ascii=False)
         fo.write((out + "\n").encode())

run('model')
run('data')
run('source')