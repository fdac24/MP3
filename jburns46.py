import json, re
import requests
from urlextract import URLExtract
import sys, gzip


utid = 'jburns46'
base = {
    'model':'https://huggingface.co/', 
    'data': 'https://huggingface.co/datasets/', 
    'source': 'https://'
    }

post = '/raw/main/README.md'
postGH = 'blob/master/README.md'
postMain = 'blob/main/README.md' # or it could be 'blob/main/README.md'

extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'
#r1\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])[[:graph:]])+)\b'

def extractURLs (c):
 res = extU.find_urls (c)
 return res

def extractDOIs (c):
 res = re.findall (DOIpattern, c)
 return res

fo = gzip.open(f"{utid}.json.gz", 'w')

def run (tp):
   with open(r"C:\Users\jaxon\Desktop\cs545\MP3\input\jburns46_model.ahk", 'r', encoding='utf-8') as f:
      for line in f:
         line = line.strip ()
         post0 = post
         if tp == 'source':
            if ';' in line:
               ___, line = line.split(';')
            else:
               continue # Skip lines that don't have ';'
            post0 = postGH

         try:
            # Create full URL
            url = base[tp] + f"{line}{post0}"
            r = requests.get (url)

            if r.status_code == 404:
               if tp != "source":
                  continue #This is a source gh and has failed
               url = base[tp] + f"{line}{postMain}"
               try:
                  r = requests.get(url)
                  if r.status_code == 404: 
                     continue #Ok, we've tried both, fail it
               except: continue

         except:
            #print("Nothing here!")
            continue   

         #If it is github, we need to handle this
         content = r.text

         if "Not Found" in content:
            #print("This git repo doesn't exist, 404")
            continue

         urls = extractURLs(content)
         dois = extractDOIs(content)
         res = { 
            'ID': line, 
            'type': tp, 
            'url': url, 
            'content': content, 
            'links': urls, 
            'dois': dois 
            }
         #print("Extraction successfull!")
         out = json.dumps(res, ensure_ascii=False)
         fo.write((out+"\n").encode())

run('model')
run('data')
run('source')
fo.close()