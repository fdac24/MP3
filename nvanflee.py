import json, re
import requests
from urlextract import URLExtract
import sys, gzip

# Adding comment, So i can make a new pull request
utid = 'nvanflee'
base= { 'model':'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://' }
post = '/raw/main/README.md'
postGH = 'blob/master/README.md' # or it could be 'blob/main/README.md'
postGHMain = 'blob/main/README.md'

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
 post0 = post
 notfound = 0
 found = 0

 with open(f"input/{utid}_{tp}", 'r') as f:
  for line in f:
   line = line.strip ()
   if tp == 'source':
    (npapers,line) = line.split(';');
    post0 = postGH
   print(line)
   url = base[tp] + f"{line}{post0}"

   # Try except block to catch connection errors
   # Cases of commas instead of periods in the url
   try:
      r = requests.get (url)
   except requests.exceptions.ConnectionError:
      if url.find(','):
         print('[~] Comma in url. Replacing and trying again...')
         url = url.replace(',','.')
         r = requests.get (url)

         if r.status_code != 200:
            print(f"[-] ERROR AFTER RETRY {line} {tp}")
      else:
         print(f"[-] CONNECTION ERROR: {line} {tp}")
   except:
      print(f"[-] ERROR: {line} {tp}")

   #If the status code is not 200, retries with main instead of master
   if r.status_code != 200 and tp == 'source':
      print(f'[#] No readme found in master for {url}, request status: {r.status_code}. Retrying with new url variant...')
      url = base[tp] + f"{line}{postGHMain}"

      # If the url contains a comma, replaces it with a period
      # This is here for the cases a comma is present and master readmes are not found
      if url.find(','):
         url = url.replace(',','.')
      
      # Try except block needed here as there have been cases of different characters being used for . in urls
      try:
         r = requests.get (url)
      except requests.exceptions.ConnectionError:
         print(f'[-] CONNECTION ERROR: {line} {tp}')
      except:
         print(f"[-] ERROR: {line} {tp}")
      
      if r.status_code != 200:
         print(f"[#] No readme with variant {line} {tp}")
   
   if r.status_code == 200:
      found += 1
      content = r.text;

      #Removes new lines from the content
      content = content.replace('\n',' ')

      urls = extractURLs(content)
      dois = extractDOIs(content)
   else:
      notfound += 1
      content = 'No Readme found.'
      urls = []
      dois = []

   res = { 'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois }
   out = json.dumps(res, ensure_ascii=False)
   fo.write((out+"\n").encode())
 print(f"[+] {found} out of {notfound+found} entries were found in {tp}.")

run('model')
run('data')
run('source')