import json, re, requests, gzip
from urlextract import URLExtract

# User setup
utid = 'rfranqui'
base = {
    'model': 'https://huggingface.co/', 
    'data': 'https://huggingface.co/datasets/', 
    'source': 'https://'
}
post = '/raw/main/README.md'
post_gh = 'blob/master/README.md'

# Initialize URL and DOI extraction
extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'

def extractURLs(c):
    return extU.find_urls(c)

def extractDOIs(c):
    return re.findall(DOIpattern, c, re.IGNORECASE)

fo = gzip.open(f"output/{utid}.json.gz", 'wt', encoding='utf-8')

def fetch_readme(url): # here we check to see if we can reach the URL, if we cant, we leave the content section as "Not Found" and move on
    try:
        r = requests.get(url)
        r.raise_for_status()
        return r.text.replace('\n', ' ')
    except requests.RequestException:
        return "Not found"

def run(tp):
    post0 = post
    with open(f"input/{utid}_{tp}.txt", 'r') as f: # please note I downloaded the files to work on my own machine and they were downloaded as .txt
        for line in f:
            line = line.strip()
            if tp == 'source':
                _, line = line.split(';', 1)
                post0 = post_gh
            url = base[tp] + f"{line}{post0}"
            content = fetch_readme(url)
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
            fo.write((out+ "\n"))

# Run for each type of entry
run('model')
run('data')
run('source')

fo.close()
