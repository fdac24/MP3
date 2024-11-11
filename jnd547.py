import json, re
import requests
from urlextract import URLExtract
import sys, gzip


utid = 'jnd547'
base= { 'model':'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://' }
post = '/raw/main/README.md'
postGH = '/blob/master/README.md' 
postGHMain = '/blob/main/README.md'

extU = URLExtract()

# Regex patterns (sourced from the internet)
DOIpattern = re.compile(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', re.IGNORECASE)
BIBpattern = r'@[\w]+\{(?:[^{}]*\{[^{}]*\})*[^}]*\}'


def extractURLs (c):
 res = extU.find_urls (c)
 return res

def extractDOIs (c):
 res = re.findall (DOIpattern, c)
 return res

def extractBIBs (c):
 res = re.findall (BIBpattern, c)
 return res


fo = gzip.open(f"output/{utid}.json.gz", 'w')

# Function for scraping all the README.md files in the repos
def run (tp):
    post0 = post
    with open(f"input/{utid}_{tp}", 'r') as f:
        for line in f:
            line = line.strip ()
            if tp == 'source':
                (_, line) = line.split(';')
                post0 = postGH
            print(line)
            url = base[tp] + f"{line}{post0}"
            print(f"trying: {url}")
            r = requests.get (url)


            # Accounting for not found errors
            if r.status_code == 404:
                if tp != 'source':
                    continue

                # Trying main instead of master
                url = base[tp] + f"{line}{postGHMain}"   
                print(f"trying: {url}") 
                r = requests.get (url)

                if r.status_code == 404: 
                    print("not found\n\n")
                    continue
                
            # Removing newlines from content
            content = r.text.replace('\n', '').replace('\r', '')

            urls = extractURLs(content)
            dois = extractDOIs(content)
            bibs = extractBIBs(content)

            res = { 'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois, 'bibs': bibs }
            out = json.dumps(res, ensure_ascii=False)
            fo.write((out+"\n").encode())

# Running the scraping for all three files
run('model')
run('data')
run('source')
fo.close()