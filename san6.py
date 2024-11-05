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
endpoints = {
    'default': '/raw/main/README.md',
    'github': '/blob/master/README.md',
    'github_main': '/blob/main/README.md'
}

# Initialize URL extractor and regular expressions for DOIs and BibTeX entries
url_extractor = URLExtract()
doi_pattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b'
bibtex_pattern = r'@\w+\{[^}]+\}'

# Define extraction functions
def extract_urls(content):
    return url_extractor.find_urls(content)

def extract_dois(content):
    return re.findall(doi_pattern, content)

def extract_bibtex(content):
    return re.findall(bibtex_pattern, content, re.DOTALL)

# Main function to process each file type and fetch README content
def process_type(file_type):
    input_file = f"input/{user_id}_{file_type}.txt"
    output_file = f"output/{user_id}.json.gz"

    with open(input_file, 'r', encoding='utf-8') as infile, gzip.open(output_file, 'wt', encoding='utf-8') as outfile:
        for line in infile:
            line = line.strip()
            endpoint = endpoints['default']

            # Handle GitHub-specific URL endpoint changes
            if file_type == 'source':
                _, line = line.split(';')
                endpoint = endpoints['github']

            # Build the full URL based on the file type and handle GitHub branch variations
            url = f"{base_urls[file_type]}{line}{endpoint}"
            response = requests.get(url)
            if response.status_code == 404 and file_type == 'source':
                url = f"{base_urls[file_type]}{line}{endpoints['github_main']}"
                response = requests.get(url)
            if response.status_code == 404:
                continue  # Skip if URL does not exist

            content = response.text
            data_entry = {
                'ID': line,
                'type': file_type,
                'url': url,
                'content': content.replace('\n', ' '),
                'links': extract_urls(content),
                'dois': extract_dois(content),
                'bibs': extract_bibtex(content)
            }

            # Write data entry to output in JSON format
            json.dump(data_entry, outfile, ensure_ascii=False)
            outfile.write('\n')

# Run the processing function for each file type
for file_type in ['model', 'data', 'source']:
    process_type(file_type)
