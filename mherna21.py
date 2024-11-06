import json, re
import requests
from urlextract import URLExtract
import sys, gzip

utid = 'mherna21'
base = { 'model': 'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://raw.githubusercontent.com/' }
post = '/raw/main/README.md'
postGHMaster = '/master/README.md' 
postGHMain = '/main/README.md'

extU = URLExtract()

# Regular expressions to match DOIs and BIBs entries
DOIpattern = re.compile(r'\b(10\.\d{4,9}/[-._;()/:A-Z0-9]+)\b', re.IGNORECASE)
BIBpattern = re.compile(r'@[\w]+\{[^{}]+\{[^{}]*\}(?:[^{}]*\{[^{}]*\})*[^}]*\}', re.DOTALL) # Got this from the internet

def extractURLs(c):
    res = extU.find_urls(c)
    return res

def extractDOIs(c):
    res = re.findall(DOIpattern, c)
    return res

def extractBIBs(c): 
    res = re.findall(BIBpattern, c)
    return res

# Open a compressed JSON file
with gzip.open(f"output/{utid}.json.gz", 'wb') as fo:

    # Function to extract content from the GitHub or HuggingFace repositories' README and write it to the compressed JSON file
    def run(tp):
        post0 = post
        # Opening the files in the input folder corresponding to my netID containing part of the url for different GitHub or HuggingFace repositories' README
        with open(f"input/{utid}_{tp}", 'r') as f:
            for line in f:
                line = line.strip()

                # If working with GitHub repositories' README
                if tp == 'source':
                    (_, line) = line.split(';')
                    # Replacing only the first occurrence of github.com/
                    line = line.replace("github.com/", "", 1)
                    post0 = postGHMaster
                print(line)

                # Set initial URL
                url = base[tp] + f"{line}{post0}"

                # Try accessing the URL
                try:
                    r = requests.get(url)

                    # If 404 is encountered for GitHub repos, retry with "main" branch
                    if r.status_code == 404 and tp == "source":
                        url = base[tp] + f"{line}{postGHMain}"
                        r = requests.get(url)

                    # Capture the content of the response
                    # Captures succesful responses for any repo either from GitHub or HuggingFace
                    if r.status_code == 200:
                        content = r.text
                    #  If not succesful response, either from GitHub or HuggingFace, write the error to the compressed JSON file   
                    else:
                        content = f"Error {r.status_code}: Unable to retrieve content."

                # Captures any other error
                except requests.RequestException as e:
                    content = f"Error: {str(e)}"

                # Extract URLs, DOIs, and BIBs
                urls = extractURLs(content)
                dois = extractDOIs(content)
                bibs = extractBIBs(content)
                res = {
                    'ID': line,
                    'type': tp,
                    'url': url,
                    'content': content,
                    'links': urls,
                    'dois': dois,
                    'bibs': bibs
                }

                # Write the JSON data to the gzip file
                out = json.dumps(res, ensure_ascii=False).encode('utf-8')
                fo.write(out)

    # Call the run() function to extract the content of README files from HuggigFace models or datasets or GitHub repos. 
    run('model')
    run('data')
    run('source')