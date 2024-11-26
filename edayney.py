import json
import re
import requests
from urlextract import URLExtract
import gzip
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

# User ID and URL templates
USER_ID = 'edayney'
URL_BASE = {
    'model': 'https://huggingface.co/',
    'data': 'https://huggingface.co/datasets/',
    'source': 'https://'
}
RAW_SUFFIX = '/raw/main/README.md'
GH_SUFFIX = 'blob/master/README.md'

# Regex patterns for extraction
DOI_REGEX = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'
BIB_PATTERN = r'@[\w]+\{[^}]+\}'

# Thread-safety for writing output
output_lock = Lock()

# Helper: Extract URLs using URLExtract
def get_urls(content):
    extractor = URLExtract()
    return extractor.find_urls(content)

# Helper: Extract DOIs using regex
def get_dois(content):
    return re.findall(DOI_REGEX, content)

# Helper: Extract bibliographies using regex
def get_bibs(content):
    return re.findall(BIB_PATTERN, content, flags=re.DOTALL)

# Function to process a single line (fetch and extract details)
def process_entry(task):
    line, data_type = task
    line = line.strip()
    suffix = RAW_SUFFIX if data_type != 'source' else GH_SUFFIX
    if data_type == 'source':
        _, line = line.split(';')

    full_url = f"{URL_BASE[data_type]}{line}{suffix}"
    print(f"Processing URL: {full_url}")

    try:
        response = requests.get(full_url)
        response_content = response.text
        urls = get_urls(response_content)
        dois = get_dois(response_content)
        bibs = get_bibs(response_content)
    except Exception as error:
        print(f"Error fetching {line}: {error}")
        response_content, urls, dois, bibs = '', [], [], []

    # Result to store
    result = {
        'Identifier': line,
        'Category': data_type,
        'URL': full_url,
        'Content': response_content,
        'Links': urls,
        'DOIs': dois,
        'Bibliographies': bibs
    }

    # Write result to output file in a thread-safe manner
    with output_lock:
        OUTPUT_FILE.write((json.dumps(result, ensure_ascii=False) + "\n").encode())

# Function to manage a category (model/data/source)
def process_category(data_type):
    input_file_path = f"input/{USER_ID}_{data_type}"
    with open(input_file_path, 'r') as file:
        tasks = [(line, data_type) for line in file.readlines()]

    # Parallel processing with threads
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(process_entry, tasks)

# Main output file setup (GZIP)
OUTPUT_FILE = gzip.open(f"output/{USER_ID}.json.gz", 'wb')

# Process categories
process_category('model')
process_category('data')
process_category('source')

# Close output file
OUTPUT_FILE.close()
