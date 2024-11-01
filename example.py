import json, re
import requests
from urlextract import URLExtract
import sys, gzip


utid = 'knguye34'
base = {
   'model': 'https://huggingface.co/',
   'data': 'https://huggingface.co/datasets/',
   'source': 'https://'
}
post = '/raw/main/'
# postGH = '/blob/' # or it could be 'blob/main/README.md'

extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'
#r1\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])[[:graph:]])+)\b'

# Authentication with Hugging Face access token
HF_TOKEN = "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"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

def extractURLs (c):
   res = extU.find_urls (c)
   return res

def extractDOIs (c):
   res = re.findall (DOIpattern, c)
   return res

fo = gzip.open(f"output/{utid}.json.gz", 'w')

def run(tp):
   branches = ['master', 'main']  # Only used for GitHub (source)
   possible_readme_files = [
        'README.md',
        'readme.md',
      #   'README.txt',
        'readme.txt'
    ]  # Add more variations as needed

   with open(f"input/{utid}_{tp}", 'r') as f:
      for line in f:
         line = line.strip()
         if tp == 'source':
            npapers, line = line.split(';')
            branch_variants = branches
         else:
            # For Hugging Face, don't vary branches, use the default
            branch_variants = ['']
         
         # Try each possible README file name
         content = None
         for branch in branch_variants:
            for readme_file in possible_readme_files:
               if tp == 'source' and branch:  # For GitHub, include branch in URL
                  url = base[tp] + f"{line}/blob/{branch}/{readme_file}"
                  r = requests.get(url)
               else:
                  url = base[tp] + f"{line}{post}{readme_file}"
                  r = requests.get(url, headers=headers)  # Include headers for authentication for huggingface 
               
               if r.status_code == 404:
                  continue  # Try the next README file variation
               
               content = r.text
               break
            
            if content:
               break # Exit the branch loop if README found
         
         if content is None:
            print(f"404 Error: {url}")
            continue  # Skip this entry if no README file was found
         
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
         out = json.dumps(res, ensure_ascii=False)
         fo.write((out + "\n").encode())

run('model')
run('data')
run('source')