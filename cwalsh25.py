import json, re
import requests
from urlextract import URLExtract
import gzip

utid = 'cwalsh25'
base = {
    'model': 'https://huggingface.co/',
    'data': 'https://huggingface.co/datasets/',
    'source': 'https://'
}
post = '/raw/main/README.md'
postGH = '/blob/master/README.md'  # Updated to ensure it starts with '/'

extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'

def extractURLs(c):
    """Extract URLs from content."""
    return extU.find_urls(c)

def extractDOIs(c):
    """Extract DOIs from content."""
    return re.findall(DOIpattern, c)

# Create output file with your identifier
with gzip.open(f"output/{utid}.json.gz", 'w') as fo:

    def run(tp):
        post0 = post
        with open(f"input/{utid}_{tp}", 'r') as f:
            for line in f:
                line = line.strip()
                
                # Handle 'source' type URLs differently for GitHub
                if tp == 'source':
                    if ';' in line:
                        _, line = line.split(';')
                    post0 = postGH  # Use GitHub-specific path

                # Construct the URL
                url = base[tp] + f"{line}{post0}"
                print(f"Constructed URL: {url}")  # Log each constructed URL

                try:
                    # Fetch README content
                    r = requests.get(url)
                    
                    # Check if the URL is valid and if it resolved correctly
                    if r.status_code != 200:
                        print(f"Warning: Failed to fetch URL {url} (Status code: {r.status_code})")
                        continue

                    content = r.text
                    urls = extractURLs(content)
                    dois = extractDOIs(content)

                    # Construct result dictionary
                    res = {
                        'ID': line,
                        'type': tp,
                        'url': url,
                        'content': content,
                        'links': urls,
                        'dois': dois
                    }

                    # Write each entry as a JSON line
                    out = json.dumps(res, ensure_ascii=False)
                    fo.write((out + "\n").encode())

                except requests.exceptions.RequestException as e:
                    # Handle connection errors or invalid URLs
                    print(f"Error: Could not retrieve {url}. Error: {e}")
                    continue

    # Run the script for 'model' and 'data'
    run('model')
    run('data')
    run('source')
