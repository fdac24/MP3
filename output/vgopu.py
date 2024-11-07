import os
import json, re
import requests
from urlextract import URLExtract
import gzip

# Set your netid
utid = 'vgopu'

# Define base URLs for model, data, and GitHub source
base = { 'model':'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://' }
post_model_data = '/raw/main/README.md'
post_github = '/blob/master/README.md'  # Use master branch by default; switch to main if needed

# Initialize URL extractor and DOI pattern
extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'

def extract_urls(content):
    """Extract URLs from content."""
    return extU.find_urls(content)

def extract_dois(content):
    """Extract DOIs from content."""
    return re.findall(DOIpattern, content)

# Ensure output directory exists
os.makedirs("output", exist_ok=True)

# Open output file for compressed JSON writing
fo = gzip.open(f"output/vgopu.json.gz", 'w')

def process_file(file_type, post_suffix):
    """Process each entry in the input file based on the type (model, data, or source)."""
    with open(f"input/{utid}_{file_type}", 'r') as f:
        for line in f:
            line = line.strip()
            if file_type == 'source':
                # Split to handle GitHub source with prefix number
                npapers, line = line.split(';')
                url = f"https://{line}{post_github}"
            else:
                url = base[file_type] + f"{line}{post_suffix}"
            
            try:
                print(f"Fetching {url}...")
                response = requests.get(url)
                response.raise_for_status()
                content = response.text
                
                # Extract URLs, DOIs, and prepare JSON entry
                urls = extract_urls(content)
                dois = extract_dois(content)
                entry = {
                    'ID': line,
                    'type': file_type,
                    'url': url,
                    'content': content.replace('\n', ' '),  # Flatten newlines
                    'links': urls,
                    'dois': dois
                }
                out = json.dumps(entry, ensure_ascii=False)
                fo.write((out + "\n").encode())
            except requests.RequestException as e:
                print(f"Error fetching {url}: {e}")

# Process each file type
process_file('model', post_model_data)
process_file('data', post_model_data)
process_file('source', '')  # No suffix as it's handled separately in process_file

# Close the output file
fo.close()