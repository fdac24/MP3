import json
import re
import requests
from urlextract import URLExtract
import gzip
from tqdm import tqdm
import os


utid = 'pmasani'

# Base URLs for models, datasets, and source repositories
base = {
    'model': 'https://huggingface.co/',
    'data': 'https://huggingface.co/datasets/',
    'source': 'https://'
}
post = '/raw/main/README.md'
postGH = '/blob/master/README.md' 

# URL and DOI extractors
extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}/[-._;()/:A-Z0-9]+)\b'

# To extract URLs from content
def extractURLs(content):
    return extU.find_urls(content)

# To extract DOIs from content
def extractDOIs(content):
    return re.findall(DOIpattern, content)

# To correct GitHub URLs
def correct_github_url(url):
    if "githubcom" in url:
        url = url.replace("githubcom", "github.com")
    return url

# To fetch content with error handling
def fetch_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        print(f"Successfully fetched {url}")
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return None
        
# output exist or none

os.makedirs("output", exist_ok=True)

# To run the scraping process with tqdm for progress
def run(tp):
    # Check if input file exists
    input_file = f"input/{utid}_{tp}"
    if not os.path.exists(input_file):
        print(f"Input file {input_file} not found. Skipping {tp} scraping.")
        return

    post0 = post if tp in ['model', 'data'] else postGH

    # Open the input file and compressed output file
    with open(input_file, 'r') as f, gzip.open(f"output/{utid}.json.gz", 'wt', encoding='utf-8') as fo:
        lines = f.readlines()
        for line in tqdm(lines, desc=f"Processing {tp} URLs"):
            line = line.strip()
            if not line:
                continue

            # Handle source-specific URL correction
            if tp == 'source':
                try:
                    number, url_part = line.split(';')
                    url_part = correct_github_url(url_part)
                except ValueError:
                    print(f"Skipping malformed line: {line}")
                    continue
                url = base[tp] + url_part + post0
            else:
                # Prepend the appropriate base URL for models and data
                url = base[tp] + line + post0

            # Fetch the content
            content = fetch_content(url)
            if content is None:
                print(f"Failed to fetch content for {line}")
                continue  # Skip if content couldn't be fetched

            # Extract URLs and DOIs
            urls = extractURLs(content)
            dois = extractDOIs(content)

            # Create a dictionary for the scraped data
            res = {
                'id': line,
                'type': tp,
                'url': url,
                'content': content.replace('\n', ' '),
                'links': urls,
                'dois': dois,
                'bibs': [] # For BibTeX entries
            }

            # Write the result to the compressed JSON file
            fo.write(json.dumps(res, ensure_ascii=False) + "\n")

# Run the script for model, data and source
run('model')
run('data')
run('source')
print("Data scraping and extraction done!")
