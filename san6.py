import json
import re
import requests
import gzip
from urlextract import URLExtract

# Define user-specific identifiers and base URL configurations
user_id = 'san6'
base_urls = {
    'model': 'https://huggingface.co/',
    'data': 'https://huggingface.co/datasets/',
    'source': 'https://'
}
post_paths = {
    'default': '/raw/main/README.md',
    'github_master': '/blob/master/README.md',
    'github_main': '/blob/main/README.md'
}

# Initialize URL extractor and regular expressions for DOIs
url_extractor = URLExtract()
doi_pattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b'

# Define extraction functions
def extract_urls(content):
    return url_extractor.find_urls(content)

def extract_dois(content):
    return re.findall(doi_pattern, content, re.IGNORECASE)

# Main function to process each file type and fetch README content
def process_type(file_type):
    input_file = f"input/{user_id}_{file_type}"
    output_file = f"output/{user_id}.json.gz"

    with open(input_file, 'r', encoding='utf-8') as infile, gzip.open(output_file, 'wt', encoding='utf-8') as outfile:
        for line in infile:
            line = line.strip()
            post_path = post_paths['default']

            # Handle GitHub-specific URL endpoint changes
            if file_type == 'source':
                _, line = line.split(';')
                post_path = post_paths['github_master']

            # Build the full URL based on the file type and handle GitHub branch variations
            url = f"{base_urls[file_type]}{line}{post_path}"
            response = requests.get(url)
            # Check if GitHub link fails with 404, and try alternate branch
            if response.status_code == 404 and file_type == 'source':
                url = f"{base_urls[file_type]}{line}{post_paths['github_main']}"
                response = requests.get(url)
            if response.status_code == 404:
                print(f"URL not found: {url}")
                continue  # Skip to the next entry if URL is unavailable

            content = response.text
            data_entry = {
                'ID': line,
                'type': file_type,
                'url': url,
                'content': content.replace('\n', ' '),
                'links': extract_urls(content),
                'dois': extract_dois(content)
            }

            # Write data entry to output in JSON format
            json.dump(data_entry, outfile, ensure_ascii=False)
            outfile.write('\n')

# Run the processing function for each file type
for file_type in ['model', 'data', 'source']:
    process_type(file_type)
