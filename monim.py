# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 23:06:17 2024

@author: monim
"""


import json, re
import requests
from urlextract import URLExtract
import sys, gzip
from tqdm import tqdm

utid = 'monim'
base= { 'model':'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://' }
post = '/raw/main/README.md'
postGH = 'blob/master/README.md'
postGH_1 =  'blob/main/README.md' #handling the case for main/master

extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'
bibPattern = r'@(\w+)\{[^}]+\}' #bonus problem

def extractURLs (c):
 res = extU.find_urls (c)
 return res

def extractDOIs (c):
 res = re.findall (DOIpattern, c)
 return res

def extractBibs (c):
 res = re.findall (bibPattern, c)
 return res

fo = gzip.open(f"output/{utid}.json.gz", 'w+')

def run (tp):
   post0 = post
   with open(f"input/{utid}_{tp}", 'r') as f:
      for line in tqdm(f):
         line = line.strip ()
         if tp == 'source':
            (npapers,line) = line.split(';');
            post0 = postGH
         print(line)
         url = base[tp] + f"{line}{post0}"
         try:
            r = requests.get (url)
         except:
            continue
         if r.status_code != 200: 
            if tp != 'source':
               continue
            else:
               url_1 = url.replace(postGH, postGH_1)
               r = requests.get(url_1)
               if r.status_code != 200:
                  continue
               else:
                  url = url_1

         content = r.text
   #github returns repos that do not exist, need to detect that here
   #github when you give master instead of main, that might cause issues as well
   #fixed both
         urls = extractURLs(content)
         dois = extractDOIs(content)
         bibs = extractBibs(content)
         res = { 'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois, 'bibs': bibs }
         out = json.dumps(res, ensure_ascii=False)
         fo.write((out+"\n").encode())

run('model')

run('data')

run('source')

fo.close()
