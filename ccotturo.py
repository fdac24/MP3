import json, re
import requests
from urlextract import URLExtract
import sys, gzip


utid   = 'ccotturo'
base   = { 'model':'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://' }
post   = '/raw/main/README.md'
postGH = '/blob/master/README.md'
postGHadditional = ['/blob/main/README.md', '/blob/main/Readme.md', '/blob/main/readme.md', '/blob/main/readme',
                    '/blob/main/README', '/blob/master/Readme.md', '/blob/master/readme.md', '/blob/master/readme',
                    '/blob/master/README']

extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'
BIBpattern = r'@.*{(.*?),'

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

def run (tp):
    post0 = post
    with open(f"input/{utid}_{tp}", 'r') as f:
        for line in f:
            line = line.strip ()
            # fix some issues I encountered with the line
            if line.endswith('.git'):
                line = line[:-4]
            if line[2:12] == 'github:com':
                line = line[0:2] + 'github.com' + line[12:]
            if tp == 'source':
                (npapers,line) = line.split(';')
                post0 = postGH
            url = base[tp] + f"{line}{post0}"
            r = requests.get (url)

            # prevent errors from crashing program, ensure branch isn't renamed
            if r.status_code != 200:
                if tp != 'source':
                    continue
                is_found = False
                for post0 in postGHadditional:
                    url = base[tp] + f"{line}{post0}"
                    r = requests.get(url)
                    if r.status_code == 200:
                        is_found = True
                        break
                if not is_found:
                    print("! " + line + " not found")
                    continue
            print(tp + " | " + line)

            content = r.text;

            urls = extractURLs(content)
            dois = extractDOIs(content)
            bibs = extractBIBs(content)
            res = { 'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois, 'bibs': bibs }
            out = json.dumps(res, ensure_ascii=False)
            fo.write((out+"\n").encode())

run('model')
run('data')
run('source')