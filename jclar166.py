import json, re
import requests
from urlextract import URLExtract
import sys, gzip, os

#The code would not run without this chdir call because I was running my code on my local windows machine. I imagine it could be commented out for grading.
os.chdir("C:/Users/clark/Desktop/UTK/FDAC/MP3")

utid = 'jclar166'

base= { 'model':'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://raw.githubusercontent.com/' }

extU = URLExtract()
DOIpattern = r'10.\d{4,9}/[-._;()/:A-Z0-9]+'

'''
This specific BIBpattern was taken from the internet. It seemed to have the best results across different attempted patterns.
'''
BIBpattern = r'@[\w]+\{[^}]+\}'

post = '/raw/main/README.md'
postGHMain = '/refs/heads/main/README.md'
postGHMaster = '/refs/heads/master/README.md'


def extractURLs (c):
 res = extU.find_urls (c)
 return res

def extractDOIs (c):
 res = re.findall (DOIpattern, c, re.IGNORECASE)
 return res

def extractBIBs (c):
 res = re.findall(BIBpattern, c, re.IGNORECASE)
 return res

fo = gzip.open(f"output/anything.json.gz", 'w')

def run (tp):
   post0 = post
   with open(f"input/{utid}_{tp}", 'r') as f: #Just makes all our file operations easier.
      for line in f:
         line = line.strip()
         if tp == 'source':
            _, line = line.split(';')
            line = line[11:]
         url = base[tp] + f"{line}{post0}" if tp != 'source' else base[tp] + f"{line}{postGHMain}"
         print(url)
            
         
         r = requests.get (url)
         content = r.text

         #Removes new line characters, as specified on the MP3 README
         content = content.replace('\n', ' ')
       
         urls = extractURLs(content)
         dois = extractDOIs(content)
         bibs = extractBIBs(content)

         if content == '404: Not Found':
            #We couldn't find the main branch, so now we try the master branch
            url = base[tp] + f"{line}{post}" if tp != 'source' else base[tp] + f"{line}{postGHMaster}"
            r = requests.get(url)
            content = r.text
            
            if content == "404: Not Found":
               #Neither the master nor the main branch worked, so we cannot find a README file
               content = "No README"
            
         res = { 'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois, 'bibs': bibs }
         out = json.dumps(res, ensure_ascii=False)
         fo.write((out+"\n").encode('utf-8'))

run('model')
run('data')
run('source')