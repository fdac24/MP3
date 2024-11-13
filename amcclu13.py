import json
import requests
import re
import gzip

# Configuration
netid = "amcclu13"
base_urls = {
    "model": "https://huggingface.co/",
    "data": "https://huggingface.co/datasets/",
    "source": "https://"
}

post_urls = {
    "hugging_face": "/raw/main/README.md",
    "github_master": "/blob/master/README.md",
    "github_main": "/blob/main/README.md"
}

# Regular expressions for extracting URLs, DOIs, and BibTeX entries
regex = {
    "url": r"https?://[^\s,]+",
    "doi": r"\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)\b",
    "bib": r"@[^}]+}"
}

# Output file
output_file = f"output/{netid}.json.gz"

def read_contents(url):
    """Attempt to fetch the content from a URL and return parsed data."""
    try:
        response = requests.get(url)
        if response.status_code in range(200, 299):  # Success codes
            content = response.text.strip()
            
            # Extract URLs, DOIs, and BibTeX entries
            urls = re.findall(regex["url"], content)
            dois = re.findall(regex["doi"], content, re.IGNORECASE)
            bibs = re.findall(regex["bib"], content, re.DOTALL)
            
            return content, urls, dois, bibs
    except requests.RequestException as e:
        print(f"Request failed for {url}: {e}")
    
    return None, [], [], []

def process_entry(line, entry_type):
    """Process a single line entry to handle different URL formats."""
    line = line.strip()
    if entry_type == "source":
        # Handle the source case with master/main branches
        parts = line.split(';', 1)
        line_id = parts[1].replace("githubcom", "github.com").strip()
        
        # Attempt both master and main branches
        links = [
            f"{base_urls[entry_type]}{line_id}{post_urls['github_master']}",
            f"{base_urls[entry_type]}{line_id}{post_urls['github_main']}"
        ]
    else:
        # For model and data types
        line_id = line
        links = [f"{base_urls[entry_type]}{line_id}{post_urls['hugging_face']}"]

    for link in links:
        content, urls, dois, bibs = read_contents(link)
        if content:
            # Return the successfully fetched data and the URL used
            return content, urls, dois, bibs, link

    # If all links fail, return None
    return None, [], [], [], None

# Main execution
with gzip.open(output_file, "wt", encoding="utf-8") as gz_file:
    for entry_type in ["model", "data", "source"]:
        input_file = f"input/{netid}_{entry_type}"
        with open(input_file, "r", encoding="utf-8") as f:
            for line in f:
                content, urls, dois, bibs, final_url = process_entry(line, entry_type)
                if content:  # Only write if content was successfully fetched
                    json_obj = {
                        "id": line.strip(),
                        "type": entry_type,
                        "url": final_url,
                        "content": content,
                        "links": urls,
                        "dois": dois,
                        "bibs": bibs
                    }
                    # Write each JSON object as a separate line in the output file
                    json.dump(json_obj, gz_file, ensure_ascii=False)
                    gz_file.write("\n")  # Newline for line-delimited JSON

print(f"Data successfully scraped and saved to {output_file}")