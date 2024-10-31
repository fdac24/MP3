import json
import re
import requests
import gzip
import os
from urlextract import URLExtract


utid = 'dpate139'
base_urls = {
    'model': 'https://huggingface.co/',
    'data': 'https://huggingface.co/datasets/',
    'source': 'https://github.com/'
}
post = '/raw/main/README.md'
postGH = 'blob/main/README.md'  
output_dir = 'output'
output_file = f"{output_dir}/{utid}.json.gz"

#checking if the output directory exists
os.makedirs(output_dir, exist_ok=True)

# URL and DOI Extraction
url_extractor = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}/[-._;()/:A-Z0-9]+)\b'

def extract_urls(content):
    return url_extractor.find_urls(content)

def extract_dois(content):
    return re.findall(DOIpattern, content, re.IGNORECASE)

def extract_bib_entries(content):
    bib_entries = re.findall(r'@(?:article|book|inproceedings){[^}]*}', content, re.DOTALL)
    return bib_entries

def process_readme(tp, line, post0):
    url = f"{base_urls[tp]}{line}{post0}"
    response = requests.get(url)

    # Check for unsuccessful requests or GitHub redirects
    if response.status_code != 200:

        if 'github.com' in url and 'blob/master/' in url:
            url = url.replace('blob/master/', 'blob/main/')
            response = requests.get(url)
            if response.status_code != 200:
                return None
        else:
            return None

    content = response.text
    urls = extract_urls(content)
    dois = extract_dois(content)
    bibs = extract_bib_entries(content)

    
    result = {
        'id': line,
        'type': tp,
        'url': url,
        'content': content.replace("\n", " "),  
        'links': urls,
        'dois': dois,
        'bibs': bibs
    }
    return result

# Main function to iterate over each type
def run(tp):
    post0 = post
    input_file = f"input/{utid}_{tp}"
    output = []

    with open(input_file, 'r') as f:
        for line in f:
            line = line.strip()
            if tp == 'source':
                npapers, line = line.split(';')
                post0 = postGH  
            
            entry = process_readme(tp, line, post0)
            if entry:
                output.append(json.dumps(entry, ensure_ascii=False))

    return output

# output function
with gzip.open(output_file, 'wt', encoding="utf-8") as fo:
    for tp in ['model', 'data', 'source']:
        entries = run(tp)
        fo.write("\n".join(entries) + "\n")

print("Extraction and compression complete. Data saved in", output_file)
