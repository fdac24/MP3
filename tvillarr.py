import json, re
import requests
import sys, gzip
import bibtexparser

from tqdm import tqdm
from urlextract import URLExtract

utid: str = 'tvillarr'
base: dict[str, str] = { 
   'model':'https://huggingface.co/', 
   'data': 'https://huggingface.co/datasets/', 
   'source': 'https://raw.githubusercontent.com/'
}

# Path to README file in a HuggingFace repo
hf_readme_path: str = '/raw/main/README.md'
# Path to raw README file in GitHub repo
gh_readme_path: str = '/master/README.md'
gh_readme_path_alt: str = '/main/README.md'

extU = URLExtract()

#r1\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])[[:graph:]])+)\b'
DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'

def extract_urls(content: str) -> list:
   '''
   Extracts URLs from provided text content

   Args:
      content (str): text to extract URLs from

   Returns:
      list: list of URLs found
   '''
   
   res = extU.find_urls(content)
   return res

def extract_dois(content: str) -> list:
   '''
   Extracts DOIs from provided content following the regexp 

   Args:
      content (str): text to extract DOIs from

   Returns:
      list: list of DOIs found
   '''
   
   res = re.findall(DOIpattern, content)
   return res

def extract_bibs(content: str) -> list:
   '''
   Extracts BIB entries from content following the regexp

   Args:
      content (str): text to extract BIBs from

   Returns:
      list: list of BIBS found 
   '''

   try: 
      b = bibtexparser.loads(content)
      bibs = b.entries
   except:
      bibs = []

   return bibs

def run(source_type: str) -> None:
   with open(f"input/{utid}_{source_type}", 'r') as f:
      for line in tqdm(f):
         line = line.strip()

         # Source (GitHub repos)
         if source_type == "source":
            # Splitting the line as source file format is num;repo
            npapers, line = line.split(';')
         
            # Not using "github.com/" from line
            current_url = f'{base[source_type]}{line[11:]}{gh_readme_path}'

         # Model and Data
         else:
            current_url = f'{base[source_type]}{line}{hf_readme_path}'

         r = requests.get(current_url)

         # If the request isn't OK; mainly used for GitHub
         if r.status_code != 200:
            if source_type == "source":
               # Trying to get main branch instead of master branch
               current_url = f'{base[source_type]}{line[11:]}{gh_readme_path_alt}'
               r = requests.get(current_url)

               # If we're okay with new URL, then continue on
               if r.status_code == 200:
                  continue
               # If not, just return URL back to original URL and request
               else:
                  current_url = f'{base[source_type]}{line[11:]}{gh_readme_path}'
                  r = requests.get(current_url)

         # print(f"Current URL: {current_url}")
         content = r.text

         urls = extract_urls(content)
         # print(f"URLS: {urls}")
         dois = extract_dois(content)
         # print(f"DOIs: {dois}")
         bibs = extract_bibs(content)
         # print(f"BIBs: {bibs}")

         res = {'ID': line, 'type': source_type, 'url': current_url, 'content': content, 'links': urls, 'dois': dois, 'bibs': bibs}

         out = json.dumps(res, ensure_ascii=False)
         output_file.write((out+"\n").encode())


output_file = gzip.open(f"output/{utid}.json.gz", 'w')

run("model")
run("data")
run("source")

