import json
import re
import requests
from urlextract import URLExtract
import sys
import gzip

utid = 'cwitt8'
base = {'model': 'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://github.com'}
post = '/raw/main/README.md'
postGH = '/blob/{branch}/README.md'  # Can be 'blob/main/README.md' or 'blob/master/README.md'

extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}/[-._;()/:A-Z0-9]+)\b'

def extract_urls(content: str):
    return extU.find_urls(content)

def extract_dois(content: str):
    return re.findall(DOIpattern, content, re.IGNORECASE)

def run(tp: str):
    post0 = post
    input_file = f"input/{utid}_{tp}"
    output_file = f"output/{utid}.json.gz"
    
    with open(input_file, 'r') as f, gzip.open(output_file, 'ab') as fo:
        for line in f:
            line = line.strip().rstrip(',.;:/')
            if tp == 'source':
                (npapers, line) = line.split(';')
                post0 = postGH.format(branch='main')
                # Try main branch first, fallback to master if not found
                r = requests.get(base[tp].rstrip('/') + '/' + line.lstrip('/').lstrip('github.com/') + post0)
                if r.status_code in [404, 400]:
                    post0 = postGH.format(branch='master')
            
            url = base[tp].rstrip('/') + '/' + line.lstrip('/').lstrip('github.com/') + post0
            try:
                r = requests.get(url)
                if r.status_code == 404:
                    # Handle non-existing repositories or incorrect branches
                    print(f"Error: Repository or branch not found for URL: {url}", file=sys.stderr)
                    continue
                
                content = r.text
                urls = extract_urls(content)
                dois = extract_dois(content)
                
                res = {'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois}
                out = json.dumps(res, ensure_ascii=False)
                fo.write((out + "\n").encode())
            except requests.RequestException as e:
                print(f"Request failed for URL: {url} with error: {e}", file=sys.stderr)

# Run the function for each type
run('model')
run('data')
run('source')
