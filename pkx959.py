import json, re
import requests
from urlextract import URLExtract
import sys, gzip

utid = 'pkx959'
base= {
    'model': 'https://huggingface.co/',
    'data': 'https://huggingface.co/datasets/',
    'source': 'https://'
}
post = '/raw/main/README.md'
postGit_master = 'blob/master/README.md'  # or it could be 'blob/main/README.md'
postGit_main = 'blob/main/README.md'

extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'

def extractURLs(c):
    res = extU.find_urls(c)
    return res

def extractDOIs(c):
    res = re.findall(DOIpattern, c)
    return res

fo = gzip.open(f"output/{utid}.json.gz", 'w')

def run(tp):
    post0 = post
    with open(f"input/{utid}_{tp}", 'r') as f:
        for line in f:
            line = line.strip()
            if tp == 'source':
                (npapers, line) = line.split(';')
                post0 = postGit_master
            print(f"Done: {line}")
            url = base[tp] + f"{line}{post0}"
            r = requests.get(url)

            if r.status_code == 404:
                if tp != 'source':
                    continue
                else:
                    url = base[tp] + f"{line}{postGit_master}"
                    r = requests.get(url)
            if r.status_code != 200:
                continue

            content = r.text
            urls = extractURLs(content)
            dois = extractDOIs(content)
            res = {'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois}
            out = json.dumps(res, ensure_ascii=False)
            fo.write((out + "\n").encode())

run('model')
run('data')
run('source')
