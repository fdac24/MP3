import json, re
import requests
from urlextract import URLExtract
import sys, gzip


utid: str = 'ckornega'
baseURL: dict = { 'model':'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://' }

post: str = '/raw/main/README.md'

postGHMaster: str = 'blob/master/README.md'
postGHMain: str = 'blob/main/README.md'

extU: URLExtract = URLExtract()
DOIpattern: str = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'
#r1\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])[[:graph:]])+)\b'
BIBpattern: str = r'@\w+{.*?[\}]{2}' # Discovery

def extractURLs(c: str) -> list:
    return extU.find_urls(c)

def extractDOIs(c: str) -> list:
    return re.findall(DOIpattern, c)

def extractBIBS(c: str) ->  list:
    return re.findall(BIBpattern, c, re.DOTALL)

fo = gzip.open(f"output/{utid}.json.gz", 'w')

def run(tp: str):
    post0 = post if tp != 'source' else postGHMaster
 
    with open(f"input/{utid}_{tp}", 'r', encoding='utf8', buffering=16384) as f:
        for line in f:
            line = line.strip()
            add: str = ""
            if tp == 'source':
                npapers, line = line.split(';');
                add = "/" if line[-1] != "/" else ""

            url = baseURL[tp] + line + add
            url = url + post0
            
            try:
                r = requests.get(url)
                if r.status_code == 404:
                    if tp != 'source': continue # failure
                    url = baseURL[tp] + line  + add
                    url = url + postGHMain
                    try:
                        r = requests.get(url)
                        if r.status_code == 404: continue # failure
                    except: continue
            except: continue
                
            content = r.text;
            urls = extractURLs(content)
            dois = extractDOIs(content)
            bibs = extractBIBS(content.replace('\n', '').replace('\\n', ''))

            # bibs = [bib[:250] for bib in bibs]

            res = {
                'ID': line,
                'type': tp,
                'url': url,
                'content': content,
                'links': urls,
                'dois': dois,
                'bibs': bibs
                }
            
            out = json.dumps(res, ensure_ascii=False)
            fo.write((out+"\n").encode())
        
if __name__ == "__main__":
    run('model')
    run('data')
    run('source')
    fo.close()
    