import json, re
import requests
from urlextract import URLExtract
import sys, gzip

# User identifier
utid = 'glapham'

# Base URLs
base_urls = { 
    'model': 'https://huggingface.co/', 
    'data': 'https://huggingface.co/datasets/', 
    'source': 'https://raw.githubusercontent.com/' 
}

# URL paths
post_path = '/raw/main/README.md'
post_gh_main = '/refs/heads/main/README.md'
post_gh_master = '/refs/heads/master/README.md'

# Regular expressions for DOI and BIB identifiers
DOIpattern = r'10.\d{4,9}/[-._;()/:A-Z0-9]+'
BIBpattern = r'@[\w]+\{[^}]+\}'

# Initialize URL extractor
extU = URLExtract()

# Output gzip file
fo = gzip.open(f"output/{utid}.json.gz", 'w')

def extract_urls(content):
    return extU.find_urls(content)

def extract_dois(content):
    
    return re.findall(DOIpattern, content, re.IGNORECASE)

def extract_bibs(content):
    return re.findall(BIBpattern, content, re.IGNORECASE)

def fetch_content(url):
    """Fetch content from the provided URL."""
    response = requests.get(url)
    if response.status_code == 404:
        return "404: Not Found"
    return response.text.replace('\n', ' ').replace('"', '\"').replace("'", "\'").replace('\t', ' ').replace('\r', ' ')

def run(tp):
    """Process each type and write results to the gzip file."""
    with open(f"input/{utid}_{tp}", 'r') as f:
        for line in f:
            line = line.strip()
            if tp == 'source':
                _, line = line.split(';')
                line = line[11:]  # Extract part after 'gh/' for GitHub source

            # Construct URL based on type
            url = f"{base_urls[tp]}{line}{post_path}" if tp != 'source' else f"{base_urls[tp]}{line}{post_gh_main}"
            print(f"Processing URL: {url}")
            
            try:
                # Fetch and clean content
                content = fetch_content(url)
                
                # Try master branch if main branch is 404
                if content == "404: Not Found" and tp == 'source':
                    print("Main branch not found, trying master branch")
                    url = f"{base_urls[tp]}{line}{post_gh_master}"
                    content = fetch_content(url)
                    if content == "404: Not Found":
                        print("Master branch also not found")
                        content = "No README found"

                # Extract data
                urls = extract_urls(content) or ["No URLs found"]
                dois = extract_dois(content) or ["No DOIs found"]
                bibs = extract_bibs(content) or ["No BIBs found"]

                # Prepare result
                result = {
                    'ID': line,
                    'type': tp,
                    'url': url,
                    'content': content,
                    'links': urls,
                    'dois': dois,
                    'bibs': bibs
                }
                
                # Write result to gzip file
                fo.write((json.dumps(result, ensure_ascii=False) + "\n").encode('utf-8'))

            except Exception as e:
                print(f"Error processing {url}: {e}")
                error_result = {
                    'ID': line,
                    'type': tp,
                    'url': url,
                    'content': "None - error in reading URL",
                    'links': ["No URLs Found"],
                    'dois': ["No DOIs Found"],
                    'bibs': ["No BIBs Found"]
                }
                fo.write((json.dumps(error_result, ensure_ascii=False) + "\n").encode('utf-8'))

# Run for each type
for data_type in ['model', 'data', 'source']:
    run(data_type)

fo.close()