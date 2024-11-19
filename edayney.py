# added multi-threading to speed up the process
# finished extra credit to also extract bibs

import json, re
import requests
from urlextract import URLExtract
import sys, gzip
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock


utid = 'edayney'
base= { 'model':'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://' }
post = '/raw/main/README.md'
postGH = 'blob/master/README.md' # or it could be 'blob/main/README.md'

extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'
#r1\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])[[:graph:]])+)\b'

lock = Lock()  # To manage concurrent access to the output file


def extractURLs (c):
 res = extU.find_urls (c)
 return res

def extractDOIs (c):
 res = re.findall (DOIpattern, c)
 return res

def extractBibs(c):
    bib_pattern = r'@[\w]+\{[^}]+\}'
    res = re.findall(bib_pattern, c, flags=re.DOTALL)
    return res

fo = gzip.open(f"output/{utid}.json.gz", 'w')

def process_line(args):
    line, tp = args
    line = line.strip()
    post0 = post
    if tp == 'source':
        npapers, line = line.split(';')
        post0 = postGH
    print(f"Processing: {line}")
    url = base[tp] + f"{line}{post0}"
    try:
        r = requests.get(url)
        content = r.text
        urls = extractURLs(content)
        dois = extractDOIs(content)
        bibs = extractBibs(content)
    except Exception as e:
        print(f"Error processing {line}: {e}")
        content = ''
        urls = []
        dois = []
        bibs = []
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
    with lock:
        fo.write((out + "\n").encode())

def run(tp):
    input_file = f"input/{utid}_{tp}"
    tasks = []
    with open(input_file, 'r') as f:
        lines = f.readlines()
    args_list = [(line, tp) for line in lines]
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(process_line, args_list)

fo = gzip.open(f"output/{utid}.json.gz", 'wb')

run('model')
run('data')
run('source')

fo.close()