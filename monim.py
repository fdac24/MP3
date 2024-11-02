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
base= { 'model':'https://huggingface.co/',
       'data': 'https://huggingface.co/datasets/', 'source': 'https://' }
post = '/raw/main/README.md'
postGH = 'blob/master/README.md'
postGH_1 =  'blob/main/README.md' #handling the case for main/master

extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'
bibPattern = r'@(\w+)\s*\{\s*([^,]+),\s*(.*?)\s*\}\s*' #bonus problem

def extractURLs (c):
 res = extU.find_urls (c)
 return res

def extractDOIs (c):
 res = re.findall (DOIpattern, c)
 return res

def extractBibs (c): #for bonus
 res = re.findall (bibPattern, c)
 return res

fo = gzip.open(f"output/{utid}.json.gz", 'w+')

def run (tp):
 post0 = post
 post1 = post
 with open(f"input/{utid}_{tp}", 'r') as f:
  for line in tqdm(f):
   line = line.strip ()
   if tp == 'source':
    (npapers,line) = line.split(';');
    post0 = postGH
    post1 = postGH_1
   print(line)
   url = base[tp] + f"{line}{post0}"
   url_1 = base[tp] + f"{line}{post1}"
   try:
    r = requests.get (url)
    content = r.text
    try:
      r_1 = requests.get (url_1)
      content_1 = r_1.text
      content = content_1
    except:
      continue

    #github returns repos that do not exist, need to detect that here
    '''
    It threw error so I used a try--except block
    There it says that the url does't exist
    '''
    #github when you give master instead of main, that might cause issues as well
    urls = extractURLs(content)
    dois = extractDOIs(content)
    bibs = extractBibs(content) #for bonus
    res = { 'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois, 'bibs': bibs }
    out = json.dumps(res, ensure_ascii=False)
    fo.write((out+"\n").encode())
   except:
    print("Doesn't exist")
    continue

run('model')

run('data')

run('source')
