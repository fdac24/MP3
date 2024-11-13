import json, re
import requests
from urlextract import URLExtract
import sys, gzip


utid = 'jtayl219'
base= { 'model':'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://' }
post = '/raw/main/README.md'
postGH = 'blob/master/README.md'  # Alternative for GitHub README links

extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'
BibPattern = r'@\w+\{[^}]+\}'

def extractURLs (c):
 res = extU.find_urls (c)
 return res

def extractDOIs (c):
 res = re.findall (DOIpattern, c)
 return res

def extractBibs(content):
    return re.findall(BibPattern, content)

fo = gzip.open(f"output/{utid}.json.gz", 'w')

def run(tp):
    post0 = post
    with open(f"input/{utid}_{tp}", 'r', encoding='utf8') as f:
        for line in f:
            line = line.strip()
            if tp == 'source':
                npapers, line = line.split(';')
                post0 = postGH  
    
            url = base[tp] + f"{line}{post0}"
            r = requests.get(url)
            content = r.text
            
            if not content or r.status_code != 200:
                continue
            
            res = {
                'id': line,
                'type': tp,
                'url': url,
                'content': content.replace("\n", " "),
                'links': extractURLs(content),
                'dois': extractDOIs(content),
                'bibs': extractBibs(content)
            }
            
            fin = json.dumps(res, ensure_ascii=False)
            fo.write((fin+"\n").encode())


if __name__ == "__main__":
    run('model')
    run('data')
    run('source')
    fo.close()
