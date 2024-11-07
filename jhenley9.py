import json
import re
import requests
import gzip

# Constants for base URLs and paths
utid = 'jhenley9'
base = { 
    'model': 'https://huggingface.co/', 
    'data': 'https://huggingface.co/datasets/', 
    'source': 'https://' 
}
post_paths = { 
    'model': '/raw/main/README.md', 
    'data': '/raw/main/README.md', 
    'source': '/blob/master/README.md'  # Could be '/blob/main/README.md'
}

# Regular expressions for URL and DOI extraction
URLpattern = r'(https?://[^\s]+)'  # Simple regex for URLs
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'

def extract_urls(content):
    """Extract all URLs from README content."""
    return re.findall(URLpattern, content)

def extract_dois(content):
    """Extract all DOIs from README content."""
    return re.findall(DOIpattern, content)

def process_file(tp):
    """Process a given type (model, data, source) to retrieve and parse README files."""
    post = post_paths[tp]
    results = []
    
    with open(f"input/{utid}_{tp}.txt", 'r') as f:
        for line in f:
            entry = line.strip()
            
            # Handle 'source' type file format
            if tp == 'source':
                npapers, entry = entry.split(';')
                post = post_paths['source']  # Adjust post path for GitHub sources
            
            # Formulate URL and fetch README
            url = base[tp] + f"{entry}{post}"
            response = requests.get(url)
            if response.status_code != 200:
                print(f"Failed to retrieve README for {entry} in {tp}")
                continue
            
            content = response.text.replace('\n', ' ')
            urls = extract_urls(content)
            dois = extract_dois(content)
            
            result = {
                'id': entry,
                'type': tp,
                'url': url,
                'content': content,
                'links': urls,
                'dois': dois,
                'bibs': []
            }
            results.append(json.dumps(result, ensure_ascii=False))
    
    return results

# Write results to compressed JSON file
with gzip.open(f"output/{utid}.json.gz", 'wt', encoding="utf-8") as fo:
    for tp in ['model', 'data', 'source']:
        entries = process_file(tp)
        fo.write("\n".join(entries) + "\n")

