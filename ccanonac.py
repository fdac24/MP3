from urlextract import URLExtract
import requests
import json
import gzip
import re

utid = 'ccanonac'
base = {'model' : 'https://huggingface.co/', 'data' : 'https://huggingface.co/datasets/', 'source' : 'https://'}
post_main = '/raw/main/README.md'
post_master = '/raw/master/README.md'
postGH_master = '/raw/master/README.md'
postGH_main = '/raw/main/README.md'

extU = URLExtract()
DOIpattern = r'\b10\.\d{4,9}/[-.;()/:\w]+'
BIBpattern = r'@\w+\{(,|[^[},]|},)+}(,*\s*)\n}'

def extractURLs(c):
  res = extU.find_urls(c)
  return res

def extractDOIs(c):
  res = re.findall(DOIpattern, c)
  return res

def extractBIBs(c):
  it = re.finditer(BIBpattern, c, re.IGNORECASE)
  res = [i.group(0) for i in it]
  return res

fo = gzip.open(f"output/{utid}.json.gz", 'w')

def run(tp):
  with open(f"input/{utid}_{tp}", 'r') as f:
    for line in f:
      line = line.strip().partition('#')[0]
      if tp == 'source':
        (npapers, line) = line.split(';')
        post0 = postGH_master
      else:
        post0 = post_main
      url = f"{base[tp]}{line}{post0}"
      print(url)
      response = requests.get(url)
      
      # try other urls after errors
      if response.status_code != 200:
        print(response.status_code)
        post0 = postGH_main if tp == 'source' else post_master
        url = f"{base[tp]}{line}{post0}"
        response = requests.get(url)
        if response.status_code != 200:
          print(response.status_code)
          continue
      
      content = response.text
      urls = extractURLs(content)
      dois = extractDOIs(content)
      bibs = extractBIBs(content)
      res = {'ID' : line, 'type' : tp, 'url' : url, 'content' : content.replace("\n", " "), 'links' : urls, 'dois' : dois, 'bibs' : bibs}
      out = json.dumps(res, ensure_ascii=False)
      fo.write((out+"\n").encode())

run('model')
run('data')
run('source')