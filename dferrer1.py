import json, re
import requests
from urlextract import URLExtract
import sys, gzip


utid = 'dferrer1'
base= { 'model':'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://' }
post = '/raw/main/README.md'
postGH = 'blob/master/README.md'
postGHmain = 'blob/main/README.md'

extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'
BIBpattern = r'```bibtex([^```]*)'
BIBpattern2 = r'(@[^@]*)'

def extractURLs (c):
    res = extU.find_urls (c)
    return res

def extractDOIs (c):
    res = re.findall (DOIpattern, c)
    return res

def extractBIBs (c):
    res = re.findall(BIBpattern, c)
    
    if res == []:
        return res
    
    res2 = re.findall(BIBpattern2, res[0])
    
    if res2 == []:
        print(f"|||{res[0]}|||")
        exit()
    
    return res2

fo = gzip.open(f"output/{utid}.json.gz", 'w')

def run (tp):
    # initialize post to raw as default
    post0 = post
    a=0
    # open input file for reading
    with open(f"input/{utid}_{tp}", 'r') as f:
        for line in f:
            line = line.strip ()
            
            #  check type
            if tp == 'source':
                (npapers,line) = line.split(';')
                post0 = postGH
            print(line)
            
            # Send request, skip if an error occurs
            url = base[tp] + f"{line}{post0}"
            try:
                r = requests.get (url)
            except:
                print(f"Invalid URL: {url}")
                continue
            
            #github returns repos that do not exist, need to detect that here
            if r.status_code == 404:
                
                # check type, skip if not source type
                if tp == "source":
                    #github when you give master instead of main, that might cause issues as well
                    url = base[tp] + f"{line}{postGHmain}"
                    r = requests.get (url)
                    
                    if r.status_code == 404:
                        continue
                else:
                    continue
            else:
                content = r.text

            
            # Parse from content
            urls = extractURLs(content)
            dois = extractDOIs(content)
            bibs = extractBIBs(content)
            
            # Create JSON entry and write to file
            res = { 'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois, 'bibs': bibs }
            out = json.dumps(res, ensure_ascii=False)
            fo.write((out+"\n").encode())

run('model')
run('data')
run('source')
fo.close()