# Griffin Lee
# MP3 FDAC24

import json, re
import requests
from urlextract import URLExtract
import sys, gzip
import os

utid = 'glee30'
base = {
    'model': 'https://huggingface.co/',
    'data': 'https://huggingface.co/datasets/',
    'source': 'https://' 
}
post = '/raw/main/README.md'
postGH = '/blob/master/README.md'
extU = URLExtract()
DOIpattern = r'\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b'

def extractURLs(c):
    res = extU.find_urls(c)
    return res
def extractDOIs(c):
    res = re.findall(DOIpattern, c, re.IGNORECASE)
    return res
def extractBibs(c):
    # extract bib entries
    bib_pattern = r'@[\w]+\{[^}]+\}'
    res = re.findall(bib_pattern, c)
    return res

# ensure the output directory exists and open the output file
os.makedirs('output', exist_ok=True)
fo = gzip.open(f"output/{utid}.json.gz", 'wt', encoding='utf-8')
def run(tp):
    post0 = post
    input_file = f"input/{utid}_{tp}"
    if not os.path.exists(input_file):
        print(f"Input file {input_file} does not exist. Skipping {tp}.")
        return
    with open(input_file, 'r') as f:
        for line in f:
            line = line.strip()
            if tp == 'source':
                if ';' in line:
                    (_, line) = line.split(';')
                post0 = postGH
                # construct the URL
                url = base[tp] + f"{line}{post0}"
                r = requests.get(url)
                if r.status_code == 200:
                    match = re.search(r'href="(\/{0}\/raw\/[^"]+)"'.format(re.escape(line)), r.text)
                    if match:
                        raw_url = 'https://github.com' + match.group(1)
                        # get raw content
                        r = requests.get(raw_url)
                        if r.status_code == 200:
                            content = r.text
                        else:
                            print(f"Could not retrieve raw README for {line}")
                            continue
                    else:
                        print(f"Could not find raw content link for {line}")
                        continue
                else:
                    post0 = postGH.replace('master', 'main')
                    url = base[tp] + f"{line}{post0}"
                    r = requests.get(url)
                    if r.status_code == 200:
                        match = re.search(r'href="(\/{0}\/raw\/[^"]+)"'.format(re.escape(line)), r.text)
                        if match:
                            raw_url = 'https://github.com' + match.group(1)
                            # get raw content
                            r = requests.get(raw_url)
                            if r.status_code == 200:
                                content = r.text
                            else:
                                print(f"Could not retrieve raw README for {line}")
                                continue
                        else:
                            print(f"Could not find raw content link for {line}")
                            continue
                    else:
                        # repo doesn't exist OR no README.md
                        print(f"Could not retrieve README for {line}")
                        continue
            else:
                url = base[tp] + f"{line}{post0}"
                r = requests.get(url)
                if r.status_code != 200:
                    print(f"Could not retrieve README for {line}")
                    continue
                content = r.text
            # remove the new lines
            content = content.replace('\n', ' ').replace('\r', ' ')
            urls = extractURLs(content)
            dois = extractDOIs(content)
            bibs = extractBibs(content)
            res = {'id': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois, 'bibs': bibs}
            out = json.dumps(res, ensure_ascii=False)
            fo.write(out + "\n")
run('model')
run('data')
run('source')
fo.close()

