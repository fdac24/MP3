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

def extractURLs(c: str) -> list:
    res = extU.find_urls(c)
    return res

def extractDOIs(c: str) -> list:
    res = re.findall(DOIpattern, c)
    return res

fo = gzip.open(f"output/{utid}.json.gz", 'w')

def run(tp: str):
    global called
    post0 = post if tp != 'source' else postGHMaster
 
    with open(f"input/{utid}_{tp}", 'r', encoding='utf8', buffering=16384) as f:
        for line in f:
            line = line.strip()
            if tp == 'source':
                npapers,line = line.split(';');

            print(line)
            url = baseURL[tp] + line
            url = url + "/" if url[-1] != "/" else "" + post0
            
            try:
                r = requests.get(url)
                if r.status_code == 404:
                    if tp != 'source': continue # failure
                    url = baseURL[tp] + line
                    url = url + "/" if url[-1] != "/" else "" + postGHMain
                    try:
                        r = requests.get(url)
                        if r.status_code == 404: continue # failure
                    except: continue
            except: continue
                
            content = r.text;
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
            fo.write((out+"\n").encode())
        
if __name__ == "__main__":
    run('model')
    run('data')
    run('source')
    fo.close()
    