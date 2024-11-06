import json, re
import requests
from urlextract import URLExtract
import sys, gzip


utid = 'aweis3'
base= { 'model':'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://' }
post = '/raw/main/README.md'
postGH = 'blob/main/README.md' # or it could be 'blob/main/README.md'

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
 with open(f"input/{utid}_{tp}", 'r') as f:
  for line in f:
   line = line.strip ()
   if tp == 'source':
    (npapers,line) = line.split(';');
    post0 = postGH
   print(line)
   url = base[tp] + f"{line}{post0}"

   #github returns repos that do not exist, need to detect that here
   #github when you give master instead of main, that might cause issues as well

   try:
      r = requests.get(url)
                
      # Check if the request was successful (status code 200)
      if r.status_code == 404:
         print(f"Error: GitHub repository {line} not found (404).")
         content = "Repository not found"
      elif r.status_code == 403:
         print(f"Error: GitHub repository {line} forbidden (403). You might be rate-limited.")
         content = "Rate limit exceeded"
      elif r.status_code != 200:
         print(f"Error: HTTP status code {r.status_code} returned for {url}.")
         content = f"Error: {r.status_code}"
      else:
         print(f"Success: GitHub repository {line} found (200)")
         content = r.text
   
      urls = extractURLs(content)
      dois = extractDOIs(content)
      res = { 'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois }
      out = json.dumps(res, ensure_ascii=False)
      fo.write((out+"\n").encode())

   except requests.exceptions.RequestException as e:
      # Handle other potential errors (e.g., network issues)
      print(f"Error: Failed to retrieve {url} due to {str(e)}")
      content = f"Error: {str(e)}"
      # If the request failed, no valid content, but still log it
      urls = []
      dois = []
      res = {'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois}
      out = json.dumps(res, ensure_ascii=False)
      fo.write((out + "\n").encode())

run('model')
run('data')
run('source')