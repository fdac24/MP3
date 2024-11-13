import requests
from bs4 import BeautifulSoup
from urlextract import URLExtract
import json
import gzip

data_ids_path = 'input/mzg857_data'
model_ids_path = 'input/mzg857_model'
source_ids_path = 'input/mzg857_source'

results = []

# get requested data for data ids
bruh=0
data_id_lines = open(data_ids_path).read().splitlines()
for data_id_line in data_id_lines:
    url = "https://huggingface.co/datasets/" + data_id_line + "/blob/main/README.md"

    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    readme_div = soup.select_one("div[class*='py-4 px-4 sm:px-6 prose hf-sanitized']")

    # Extract and print the text if the section is found
    readme_text = ''
    if readme_div:
        readme_text = readme_div.get_text(separator="\n").replace('\n', ' ')

    extractor = URLExtract()
    links = extractor.find_urls(readme_text)

    dois = []
    for link in links:
        if 'doi.org' in link:
            dois.append(link)
        
    result = {
        'id': data_id_line,
        'type': 'data',
        'url': url, # the url to the readme
        'content': readme_text, # content of readme w/o newlines
        'links': links, # all links (non dois and bib entries)
        'dois': dois, # all dois
    }

    results.append(result)
    print("bruh", bruh)
    bruh+=1

thing=0
model_id_lines = open(model_ids_path).read().splitlines()
for model_id_line in model_id_lines:
    url = "https://huggingface.co/" + model_id_line + "/blob/main/README.md"

    page = requests.get(url)   
    soup = BeautifulSoup(page.content, 'html.parser')

    readme_div = soup.select_one("div[class*='py-4 px-4 sm:px-6 prose hf-sanitized']")

        # Extract and print the text if the section is found
    readme_text = ''
    if readme_div:
        readme_text = readme_div.get_text(separator="\n").replace('\n', ' ')

    extractor = URLExtract()
    links = extractor.find_urls(readme_text)

    dois = []
    for link in links:
        if 'doi.org' in link:
            dois.append(link)
        
    result = {
        'id': data_id_line,
        'type': 'data',
        'url': url, # the url to the readme
        'content': readme_text, # content of readme w/o newlines
        'links': links, # all links (non dois and bib entries)
        'dois': dois, # all dois
    }


    results.append(result)

    print("henlo", thing)
    thing+=1

source_thing=0
source_ids_lines = open(source_ids_path).read().splitlines()
for source_id_line in source_ids_lines:

    # fix line
    semicolon_index = source_id_line.find(';')
    source_id_line = source_id_line[semicolon_index+1:]

    url = "https://" + source_id_line + "/blob/main/README.md"
    page = requests.get(url)
    if page.status_code == 404:
        url = "https://" + source_id_line + "/blob/master/README.md"
        page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')

    readme_div = soup.select_one("article[class*='markdown-body entry-content container-lg']")
    
    # Extract and print the text if the section is found
    readme_text = ''
    if readme_div:
        readme_text = readme_div.get_text(separator="\n").replace('\n', ' ')

    extractor = URLExtract()
    links = extractor.find_urls(readme_text)

    dois = []
    for link in links:
        if 'doi.org' in link:
            dois.append(link)
        
    result = {
        'id': data_id_line,
        'type': 'data',
        'url': url, # the url to the readme
        'content': readme_text, # content of readme w/o newlines
        'links': links, # all links (non dois and bib entries)
        'dois': dois, # all dois
    }

    results.append(result)

    
    print("source + ", source_thing)
    source_thing+=1

with gzip.open("output/mzg857.json.gz", "wt", encoding="utf-8") as f:
    json.dump(results, f)