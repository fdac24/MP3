import json, re
import requests
from urlextract import URLExtract
import gzip

utid = 'aroman'
base= { 'model':'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://' }
post = '/raw/main/README.md'
postGH = '/blob/master/README.md' # or it could be 'blob/main/README.md'
postGH_main = '/blob/main/README.md'

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
                (npapers,line) = line.split(';')
                post0 = postGH

            print(line)
            url = base[tp] + f"{line}{post0}"            
            try:
                r = requests.get (url)
                content = r.text

                # see if connection fails or not and making sure it's for the github links
                if r.status_code == 404 and tp == 'source':
                    # trying main instead of master for Github
                    url = base[tp] + f"{line}{postGH_main}"
                    r = requests.get(url)

                    # if the connection fails continue
                    if r.status_code == 404:
                        continue

                content = r.text
                urls = extractURLs(content)
                dois = extractDOIs(content)
                res = { 'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois }
                out = json.dumps(res, ensure_ascii=False)
                fo.write((out+"\n").encode())
            except:
                print(f'Request failed: {url}')

run('model')
run('data')
run('source')
fo.close()