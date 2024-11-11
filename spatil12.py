# import json
# import requests
# import re
# import gzip

# num = 0

# def read_contents(url):
#     global num
#     response = requests.get(url)
#     if not response.status_code == 404:
#         # Read and clean the content
#         content = response.text.strip()  # Keep newlines as they are for JSON format
#         # Extract links, DOIs, etc.
#         urls = re.findall(r'https?://[^\s]+', content)
#         dois = re.findall(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', content, re.IGNORECASE)
#         bibs = re.findall(r'@.*?\{.*?\}', content, re.DOTALL)

#         return content, urls, dois, bibs
#     else:
#         num += 1
#         print(f"{num}Failed to fetch {url} - Status code: {response.status_code}")
#     return None, [], [], []

# results = []

# # Process datasets
# with open("./input/spatil12_data", "r") as file: 
#     for line in file.readlines():
#         data_id = line.strip()
#         data_url = f"https://huggingface.com/datasets/{data_id}"
#         # print(f"Processing data URL: {data_url}")
#         content, urls, dois, bibs = read_contents(data_url)
#         results.append({
#             'ID': data_id,  # Changed 'id' to 'ID'
#             'type': 'data',
#             'url': data_url,
#             'content': content,
#             'links': urls,
#             'dois': dois,
#             'bibs': bibs
#         })

# # Process models
# with open("./input/spatil12_model", "r") as file2:
#     for line in file2.readlines():
#         model = line.strip()
#         model_url2 = f"https://huggingface.co/{model}/raw/main/README.md"
#         # print(f"Processing data URL: {model_url2}")
#         content, urls, dois, bibs = read_contents(model_url2)
#         results.append({
#             'ID': model,  # Changed 'id' to 'ID'
#             'type': 'model',
#             'url': model_url2,
#             'content': content,
#             'links': urls,
#             'dois': dois,
#             'bibs': bibs
#         })

# #process githubs
# with open("./input/spatil12_source", "r") as file3:
#     for line in file3.readlines():
#         source = line.strip()
#         # Split line by semicolon and fix missing dot in 'github com'
#         _, url_part = source.split(";", 1)
#         url_part = url_part.strip().replace("github com", "github.com")
#         source_url3 = f"https://{url_part}/blob/master/README.md"
#       #  print(f"Processing data URL: {source_url3}")
#         content, urls, dois, bibs = read_contents(source_url3)
#         results.append({
#             'ID': source,  # Changed 'id' to 'ID'
#             'type': 'source',
#             'url': source_url3,
#             'content': content,
#             'links': urls,
#             'dois': dois,
#             'bibs': bibs
#         })


# # Save results to gzip
# with gzip.open("./output/spatil12.json.gz", 'wt', encoding='utf-8') as f:
#     for entry in results:
#         json.dump(entry, f, ensure_ascii=False)
#         f.write('\n')
# print("Data extraction complete and saved to output/spatil12.json.gz.")


import json, re
import requests
from urlextract import URLExtract
import sys, gzip


utid = 'spatil12'
base= { 'model':'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://' }
post = '/raw/main/README.md'
postGH = 'blob/master/README.md' # or it could be 'blob/main/README.md'

extU = URLExtract()
DOIpattern = r'\b(10.\d{4,9}/[-.;()/:A-Z0-9]+)\b/i'
#r1\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&'<>])[[:graph:]])+)\b'

def extractURLs (c):
 res = extU.find_urls (c)
 return res

def extractDOIs (c):
 res = re.findall (DOIpattern, c)
 return res

fo = gzip.open(f"output/{utid}.json.gz", 'w')

def run (tp):
 post0 = post
 with open(f"input/{utid}_{tp}", 'r') as f:
  for line in f:
   line = line.strip ()
   if tp == 'source':
    (npapers,line) = line.split(';')
    post0 = postGH
   print(line)
   url = base[tp] + f"{line}{post0}"
   r = requests.get (url)
   content = r.text
   #github returns repos that do not exist, need to detect that here
   #github when you give master instead of main, that might cause issues as well
   urls = extractURLs(content)
   dois = extractDOIs(content)
   res = { 'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois}
   out = json.dumps(res, ensure_ascii=False)
   fo.write((out+"\n").encode())

run('model')
run('data')
run('source')
