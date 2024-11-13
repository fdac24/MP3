import json, re
import requests
from urlextract import URLExtract
import sys, gzip


utid = 'mmccor23'
base = { 'model': 'https://huggingface.co/', 
        'data': 'https://huggingface.co/datasets/', 
        'source': 'https://' }

post = '/raw/main/README.md'
postGH = 'blob/master/README.md'  # or it could be 'blob/main/README.md'
postGH_main = 'blob/main/README.md'

extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'
bib_pattern = r"@([a-zA-Z]+)\{([^}]+)\}"

# Get urls
def extractURLs(c):
    res = extU.find_urls(c)
    return res

# Get DOIs
def extractDOIs(c):
    res = re.findall(DOIpattern, c)
    return res

# Get bibs
def extractbibs(c):
    res = re.findall(bib_pattern, c)
    return res


fo = gzip.open(f"output/{utid}.json.gz", 'w')


def run(tp):
    post0 = post
    
    with open(f"input/{utid}_{tp}", 'r') as f:
        for line in f:
            line = line.strip()
            if tp == 'source':
                (npapers, line) = line.split(';')
                post0 = postGH

            print(line)
            url = base[tp] + f"{line}{post0}"
            r = requests.get(url)

            # If it recieves an error code
            if r.status_code != 200:
                # Try with main
                post0 = postGH_main
                url = base[tp] + f"{line}{post0}"
                r = requests.get(url)
                # If it still gets an error code, only print out these values. 
                if r.status_code != 200:
                    print(f"Error: Could not access {url}")
                    res = {'ID': line, 
                           'type': tp, 
                           'url': url, }
            
            # Otherwise continue as regular file 
            else:
              content = r.text
              urls = extractURLs(content)
              dois = extractDOIs(content)
              bibs = extractbibs(content)
              res = {'ID': line, 
                     'type': tp, 
                     'url': url, 
                     'content': content, 
                     'links': urls, 
                     'dois': dois, 
                     'bibs':bibs }

            out = json.dumps(res, ensure_ascii=False)
            fo.write((out + "\n").encode())

run('model')
run('data')
run('source')
fo.close()