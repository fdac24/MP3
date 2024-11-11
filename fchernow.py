import json
import re
import requests
import gzip
from urlextract import URLExtract
from pathlib import Path

# Define user ID and base URLs for Hugging Face and GitHub
utid = 'fchernow'
base = {
    'model': 'https://huggingface.co/',
    'data': 'https://huggingface.co/datasets/',
    'source': 'https://'
}
post_hf = '/raw/main/README.md'
post_gh = '/blob/main/README.md'  # or '/blob/master/README.md' if necessary

# Initialize URL extractor and DOI pattern
extU = URLExtract()
DOIpattern = r'\b(10\.\d{4,9}/[-._;()/:A-Z0-9]+)\b'
# BibTeX pattern to match entries like "@article{...}"
BibTeXPattern = r'@\w+\{[^}]+\}'

# Set a timeout for requests (in seconds)
REQUEST_TIMEOUT = 10

# Functions to extract URLs, DOIs, and BibTeX entries
def extractURLs(content):
    return extU.find_urls(content)

def extractDOIs(content):
    return re.findall(DOIpattern, content, re.IGNORECASE)

def extractBibTeX(content):
    return re.findall(BibTeXPattern, content, re.DOTALL)

# Output file for compressed JSON data
output_path = f"output_data/{utid}.json.gz"
Path("output_data").mkdir(parents=True, exist_ok=True)  # Ensure the directory exists

# Variable to track the number of successful entries
successful_entries = 0

# Open output file for writing
with gzip.open(output_path, 'wt', encoding='utf-8') as fo:

    def run(tp):
        global successful_entries  # Reference the successful_entries variable in the global scope
        # Determine which post suffix to use
        post_suffix = post_hf if tp != 'source' else post_gh

        # Open the input file based on type (model, data, or source)
        with open(f"{utid}_{tp}.txt", 'r') as f:
            line_count = 0  # Track the number of lines processed
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Handle GitHub entries in 'source'
                if tp == 'source':
                    if ';' in line:
                        npapers, line = line.split(';')
                    else:
                        continue

                # Construct the full URL for README retrieval
                url = base[tp] + f"{line}{post_suffix}"
                
                # Fetch README content with timeout
                try:
                    r = requests.get(url, timeout=REQUEST_TIMEOUT)
                    r.raise_for_status()
                    content = r.text
                    status = "success"
                except requests.RequestException:
                    content = ""
                    status = "failed"

                # Extract URLs, DOIs, and BibTeX entries from the README content
                urls = extractURLs(content)
                dois = extractDOIs(content)
                bibs = extractBibTeX(content)

                # Write the entry to output file, regardless of status
                res = {
                    'id': line,
                    'type': tp,
                    'url': url,
                    'content': content.replace("\n", " ") if content else "",
                    'links': urls,
                    'dois': dois,
                    'bibs': bibs,
                    'status': status
                }
                out = json.dumps(res, ensure_ascii=False)
                fo.write(out + "\n")

                # If the entry was successful, increment the counter
                if status == "success":
                    successful_entries += 1

                line_count += 1
            
            print(f"Processed {line_count} lines in {tp} file.")

    # Run for each type: model, data, and source
    run('model')
    run('data')
    run('source')

print(f"Data successfully saved to {output_path} with {successful_entries} successful entries.")
