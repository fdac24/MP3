import json, re, gzip
import requests
from urlextract import URLExtract

url_base = {
  'model': 'https://huggingface.co/',
  'data': 'https://huggingface.co/datasets/',
  'source': 'https://'
}
post = '/raw/main/README.md'
postGH = 'blob/master/README.md'  # or 'blob/main/README.md'

DOIpattern = r'\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i'
extU = URLExtract()

def extract_urls(text):
  return extU.find_urls(text)

def extract_dois(str):
  return re.findall(DOIpattern, str)

def entries_for_type(type):
  with open(f"input/emaness_{type}", 'r') as of:
    for line in of:
      line = line.strip()
      suffix = postGH if type == 'source' else post
      id = line.split(';')[1] if type == 'source' else line
      url = f"{url_base[type]}{id}{suffix}"
      try:
        r = requests.get(url)
      except:
        continue
      if r.status_code != 200:
        continue
      content = r.text.replace('\n', ' ')
      urls = extract_urls(content)
      dois = extract_dois(content)
      obj = {
        'id': id,
        'type': type,
        'url': url,
        'content': content,
        'links': urls,
        'dois': dois,
        'bibs': []  # bib extraction unimplemented
      }
      yield obj

with gzip.open(f"output/emaness.json.gz", 'wt', encoding='utf-8') as of:
  for type in ['model', 'data', 'source']:
    for entry in entries_for_type(type):
      json.dump(entry, of)
      of.write('\n')