import json, re
import requests
from urlextract import URLExtract
import sys, gzip


utid = 'slavey'
base = { 'model':'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://'}

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

fo = gzip.open(f"output/{utid}.json.gz", 'w')

def run (tp):
   if tp != 'source':
      post0 = post 
   else:
      post0 = postGH

   with open(f"input/{utid}_{tp}", 'r') as f:
      for line in f:
         line = line.strip ()
         if tp == 'source':
            (npapers,line) = line.split(';')
         
         #print(line)
         try:
            print(tp)
            #Detect the repos that don't exist
            url = base[tp] + f"{line}{post0}"
            #print(url)
            r = requests.get (url)
            if r.status_code == 404:
               if tp != "source":
                  #print("404")
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
         res = { 'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois }
         #print("Extraction successfull!")
         out = json.dumps(res, ensure_ascii=False)
         fo.write((out+"\n").encode())

run('model')
run('data')
run('source')
fo.close()