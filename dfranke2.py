import json
import re
import requests
import gzip
from urlextract import URLExtract

# Dillon Frankenstein
# 11/3/2024

# Define constants
netid = 'dfranke2'
base_urls = {
    'model': 'https://hf-mirror.91sky.org/',
    'data': 'https://huggingface.co/datasets/',
}
post_data = '/blob/main/README.md'  # Kept as main for Hugging Face
default_branch = 'main'  # Set default branch name

# Initialize URL extractor and DOI regex pattern
extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b'

def extract_urls(content):
    return extU.find_urls(content)

def extract_dois(content):
    return re.findall(DOIpattern, content)

def fetch_readme_content(url):
    """Fetch README content from a given URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for HTTP codes 4xx or 5xx
        return response.text
    except requests.RequestException as e:
        print(f"Failed to retrieve {url}: {e}")
        return ""

def check_url_exists(url):
    """Check if a URL exists by sending a HEAD request."""
    try:
        response = requests.head(url)
        return response.status_code == 200
    except requests.RequestException:
        return False

def process_type(file_type):
    file_path = f"input/{netid}_{file_type}"
    output_path = f"output/{netid}.json.gz"

    with open(file_path, 'r', encoding='utf-8') as f, gzip.open(output_path, 'wt', encoding='utf-8') as fo:
        for line in f:
            line = line.strip()
            if file_type == 'source':
                _, line = line.split(';', 1)  # Skip the first column

            # Determine the correct README URL based on GitHub or other links
            if "github.com" in line:
                # Adjusted to use raw URL for GitHub
                repo_parts = line.split('/')
                if len(repo_parts) >= 2:
                    owner = repo_parts[-2]
                    repo_name = repo_parts[-1]
                    readme_url = f"https://raw.githubusercontent.com/{owner}/{repo_name}/{default_branch}/README.md"  # Use default branch
                else:
                    print(f"Invalid GitHub URL format: {line}")
                    continue
            else:
                if file_type == 'model':
                    readme_url = f"{base_urls['model']}{line}/blob/{default_branch}/README.md"  # For models, still use main
                elif file_type == 'data':
                    readme_url = f"{base_urls['data']}{line}{post_data}"  # For datasets, use main
                else:
                    readme_url = f"{line}/blob/{default_branch}/README.md"  # Default to main for other sources

            print(f"Checking URL: {readme_url}")  # Debug output

            if check_url_exists(readme_url):
                content = fetch_readme_content(readme_url)
                
                urls = extract_urls(content)
                dois = extract_dois(content)

                # Prepare the data entry
                data_entry = {
                    'id': line,
                    'type': file_type,
                    'url': readme_url,
                    'content': content.replace('\n', ' '),  # Remove newlines
                    'links': urls,
                    'dois': dois,
                    'bibs': []  # Placeholder for BibTeX entries, if needed
                }

                json.dump(data_entry, fo, ensure_ascii=False)
                fo.write('\n')
            else:
                print(f"URL does not exist: {readme_url}")

# Run the process for each type
for tp in ['model', 'data', 'source']:
    process_type(tp)
