import json
import re
import requests
import gzip
from urlextract import URLExtract
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration variables
utid = 'smoparth'
input_folder = 'input'
output_folder = 'output'
base_urls = {
    'model': 'https://huggingface.co/',
    'data': 'https://huggingface.co/datasets/',
    'source': 'https://'
}
post = '/raw/main/README.md'
post_github = '/blob/master/README.md'

# Initialize URL extractor and DOI regex
url_extractor = URLExtract()
doi_pattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b'
bib_pattern = r'@[\w]+\{[^}]+\}'  # Simple bibtex entry pattern

# Output file path
output_file = f'{output_folder}/{utid}.json.gz'

def extract_urls(content):
    """Extracts URLs from the content using URLExtract."""
    try:
        return url_extractor.find_urls(content)
    except Exception as e:
        print(f"Error extracting URLs: {e}")
        return []

def extract_dois(content):
    """Extracts DOIs from the content using regex."""
    try:
        return re.findall(doi_pattern, content, re.IGNORECASE)
    except Exception as e:
        print(f"Error extracting DOIs: {e}")
        return []

def extract_bib_entries(content):
    """Extracts BibTeX entries from the content using regex."""
    try:
        return re.findall(bib_pattern, content)
    except Exception as e:
        print(f"Error extracting BibTeX entries: {e}")
        return []

def fetch_readme(url):
    """Fetches the README content from the given URL."""
    print(f"Fetching README from {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        print(f"Successfully fetched {url}")
        return response.text
    except requests.exceptions.Timeout:
        print(f"Timeout error fetching {url}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
    return None

def process_entry(entry):
    """Processes a single entry by fetching and extracting relevant information from the README."""
    entry_id, entry_type, url = entry['id'], entry['type'], entry['url']
    content = fetch_readme(url)
    if content:
        return {
            'id': entry_id,
            'type': entry_type,
            'url': url,
            'content': content.replace('\n', ' '),  # Remove newlines
            'links': extract_urls(content),
            'dois': extract_dois(content),
            'bibs': extract_bib_entries(content)
        }
    else:
        print(f"Skipping entry due to missing content for {entry_id} of type {entry_type}")
    return None

def load_items_from_file(file_path, entry_type):
    """Loads items from a .txt file based on entry type and constructs the URLs."""
    items = []
    try:
        with open(file_path, 'r') as file:
            for line_num, line in enumerate(file, start=1):
                line = line.strip()
                if not line:
                    print(f"Skipping empty line {line_num} in {file_path}")
                    continue

                if entry_type == 'source':
                    parts = line.split(';')
                    if len(parts) != 2:
                        print(f"Invalid format on line {line_num} in {file_path}: {line}")
                        continue
                    entry_id = parts[1]
                    url = base_urls[entry_type] + entry_id + post_github
                else:
                    entry_id = line
                    url = base_urls[entry_type] + entry_id + post

                if not entry_id or not url:
                    print(f"Error constructing URL for entry on line {line_num} in {file_path}")
                    continue

                items.append({'id': entry_id, 'type': entry_type, 'url': url})
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    
    return items

def main():
    # Ensure output folder exists
    import os
    os.makedirs(output_folder, exist_ok=True)

    # Define file paths
    model_file = f"{input_folder}/{utid}_model.txt"
    data_file = f"{input_folder}/{utid}_data.txt"
    source_file = f"{input_folder}/{utid}_source.txt"

    # Load items from each file
    model_items = load_items_from_file(model_file, 'model')
    data_items = load_items_from_file(data_file, 'data')
    source_items = load_items_from_file(source_file, 'source')

    # Combine all items
    items = model_items + data_items + source_items

    # Open the output file in append mode
    with gzip.open(output_file, 'at', encoding='utf-8') as f:
        # Process entries in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=24) as executor:
            future_to_entry = {executor.submit(process_entry, item): item for item in items}
            
            # Collect results as they are completed
            for future in as_completed(future_to_entry):
                result = future.result()
                if result:
                    # Write each processed entry to the file immediately
                    json.dump(result, f, ensure_ascii=False)
                    f.write('\n')
                    print(f"Written entry {result['id']} of type {result['type']} to file")

    print(f"Data processing completed. Output saved to {output_file}")

if __name__ == "__main__":
    main()
