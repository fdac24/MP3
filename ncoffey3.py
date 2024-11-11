# COSC 545 MP3
# Nolan Coffey
# netid: ncoffey3
# github: ncoffey42
# 11-6-24

import json, re
import requests
from urlextract import URLExtract
import gzip

# Use raw.githubusercontent.com instead of github.com for significantly faster scraping
utid = 'ncoffey3'
base= { 'model':'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://raw.githubusercontent.com' }
post = '/raw/main/README.md'

post_main = '/refs/heads/main/README.md'
post_master = '/refs/heads/master/README.md'

extU = URLExtract()
DOIpattern = r'10\.\d{4,9}/[-._;()/:A-Z0-9]+' #https://www.crossref.org/blog/dois-and-matching-regular-expressions/ slightly modified

def extractURLs (c):
    res = extU.find_urls (c)
    return res

def extractDOIs (c):
    res = re.findall (DOIpattern, c)
    return res

def extractBIBs(content):
    bib_entries = []
    # Regular expression to match the start of a BibTex entry
    BIBpattern = r'@[\w]+\s*\{'
    matches = re.finditer(BIBpattern, content)
    content_length = len(content)
    
    # Parse through each Bib entry, this is because they may contain nested braces that regular expresssions cannot account for
    for match in matches:
        start_index = match.start()
        brace_count = 0
        i = match.end()  # Start after opening brace {
        # Iterate through the content, checking for nested braces
        while i < content_length:
            char = content[i]
            if char == '{':
                # Use a counter to ensure that each brace is even
                brace_count += 1
            elif char == '}':
                # Bib entry closing brace
                if brace_count == 0:
                    end_index = i + 1
                    bib_entry = content[start_index:end_index]
                    bib_entries.append(bib_entry)
                    break
                else:
                    brace_count -= 1
            i += 1
        else:
            # Skip bib entry due to improper formatting leading to uneven braces
            continue 
    return bib_entries


fo = gzip.open(f"output/{utid}.json.gz", 'w')

def run (tp):
 post0 = post
 with open(f"input/{utid}_{tp}", 'r') as f:
  for line in f:
    line = line.strip ()
    print(line)
    if tp == 'source':
            (npapers,line) = line.split(';')
            # Slice github.com from source since using raw.githubusercontent.com instead
            line = line[10:]
            # URL will first search main branch for README
            url = base[tp] + f"{line}{post_main}"
            print(url)
    else:
        # Not a github page, follow default post0 format 
        url = base[tp] + f"{line}{post0}"

    r = requests.get (url)
    content = r.text
    # Remove newline characters
    content = content.replace('\n', ' ')

    if content == '404: Not Found':
        # If no README is found on main branch of a github page, try checking the master branch
        if tp == 'source':
            url = base[tp] + f"{line}{post_master}"
            print(url)
            r = requests.get (url)
            content = r.text
            content = content.replace('\n', ' ')

            # README not found
            if content == '404: Not Found':
                print("Not found")
                continue

            
        else:
            print("Not found")
            continue

    # README found, parse content
    urls = extractURLs(content)
    dois = extractDOIs(content)
    bibs = extractBIBs(content)
    res = { 'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois, 'bibs': bibs }
    out = json.dumps(res, ensure_ascii=False)
    fo.write((out+"\n").encode())

run('model')
run('data')
run('source')
fo.close()