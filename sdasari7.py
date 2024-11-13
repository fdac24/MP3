import json
import re
import requests
import gzip
from urlextract import URLExtract
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

# Configuration settings
USER_ID = 'sdasari7'
INPUT_DIR = 'input'
OUTPUT_DIR = 'output'
BASE_URLS = {
    'model': 'https://huggingface.co/',
    'dataset': 'https://huggingface.co/datasets/',
    'source': 'https://'
}
RAW_SUFFIX = '/raw/main/README.md'
GITHUB_SUFFIX = '/blob/master/README.md'
OUTPUT_FILE_PATH = f'{OUTPUT_DIR}/{USER_ID}.json.gz'

# Regular expressions
DOI_REGEX = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b'
BIBTEX_REGEX = r'@[\w]+\{[^}]+\}'  # Simple bibtex entry pattern

# Initialize URL extractor
url_extractor = URLExtract()

def extract_urls(content):
    """Extracts URLs from the content."""
    try:
        return url_extractor.find_urls(content)
    except Exception as e:
        print(f"Error extracting URLs: {e}")
        return []

def extract_dois(content):
    """Extracts DOIs from the content."""
    try:
        return re.findall(DOI_REGEX, content, re.IGNORECASE)
    except Exception as e:
        print(f"Error extracting DOIs: {e}")
        return []

def extract_bibtex_entries(content):
    """Extracts BibTeX entries from the content."""
    try:
        return re.findall(BIBTEX_REGEX, content)
    except Exception as e:
        print(f"Error extracting BibTeX entries: {e}")
        return []

def fetch_content(url):
    """Fetches content from the specified URL."""
    print(f"Fetching content from {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        print(f"Successfully fetched content from {url}")
        return response.text
    except requests.exceptions.Timeout:
        print(f"Timeout error fetching {url}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
    return None

def process_entry(entry):
    """Processes a single entry by fetching and extracting relevant information."""
    content = fetch_content(entry['url'])
    if content:
        return {
            'id': entry['id'],
            'category': entry['category'],
            'url': entry['url'],
            'content': content.replace('\n', ' '),  # Remove newlines
            'links': extract_urls(content),
            'dois': extract_dois(content),
            'bibtex_entries': extract_bibtex_entries(content)
        }
    else:
        print(f"Skipping entry due to missing content for {entry['id']} in category {entry['category']}")
    return None

def construct_url(entry_id, category):
    """Constructs URL based on entry type and ID."""
    suffix = GITHUB_SUFFIX if category == 'source' else RAW_SUFFIX
    return f"{BASE_URLS[category]}{entry_id}{suffix}"

def load_entries(file_path, category):
    """Loads entries from a file and constructs URLs."""
    entries = []
    try:
        with open(file_path, 'r') as file:
            for line_num, line in enumerate(file, start=1):
                line = line.strip()
                if not line:
                    print(f"Skipping empty line {line_num} in {file_path}")
                    continue

                if category == 'source':
                    parts = line.split(';')
                    if len(parts) != 2:
                        print(f"Invalid format on line {line_num} in {file_path}: {line}")
                        continue
                    entry_id = parts[1]
                else:
                    entry_id = line

                url = construct_url(entry_id, category)
                entries.append({'id': entry_id, 'category': category, 'url': url})
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return entries

def save_results(entries):
    """Saves processed entries to a compressed output file."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with gzip.open(OUTPUT_FILE_PATH, 'at', encoding='utf-8') as file:
        for entry in entries:
            if entry:
                json.dump(entry, file, ensure_ascii=False)
                file.write('\n')
                print(f"Saved entry {entry['id']} in category {entry['category']}")

def process_entries_in_parallel(entries):
    """Processes all entries in parallel and saves results."""
    processed_entries = []
    with ThreadPoolExecutor(max_workers=24) as executor:
        futures = [executor.submit(process_entry, entry) for entry in entries]
        for future in as_completed(futures):
            processed_entries.append(future.result())
    return processed_entries

def main():
    # File paths
    model_file_path = f"{INPUT_DIR}/{USER_ID}_model.txt"
    data_file_path = f"{INPUT_DIR}/{USER_ID}_data.txt"
    source_file_path = f"{INPUT_DIR}/{USER_ID}_source.txt"

    # Load entries from files
    entries = (
        load_entries(model_file_path, 'model') +
        load_entries(data_file_path, 'dataset') +
        load_entries(source_file_path, 'source')
    )

    # Process entries in parallel
    processed_entries = process_entries_in_parallel(entries)
    save_results([entry for entry in processed_entries if entry])

    print(f"Data processing completed. Output saved to {OUTPUT_FILE_PATH}")

if __name__ == "__main__":
    main()
