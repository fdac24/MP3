#Ryan Peruski, yhg461, COSC 545, MP3
import json, re
import requests
from urlextract import URLExtract
import sys, gzip


utid = 'yhg461'
base= { 'model':'https://huggingface.co/', 'data': 'https://huggingface.co/datasets/', 'source': 'https://raw.githubusercontent.com/' }

#Note: I take a different approach for the source data, as the URL is a raw README file, rather than GitHub itself. The reasons why I do this are:

#1. The GitHub page is way too big to try and parse over 2000 of them in a reasonable amount of time.
#2. A 404 error ALSO returns a huge page, so I can't just check if the page is empty.
#3. This runs a lot faster if I decide to run the master branch as well -- it would, again, take extremely long to try and check branches
#4. If we look at both the main and master branches, most of the README's are found in one of them, so it's a good compromise of time vs. accuracy.

#Note that this, still, takes a long time to run, so comment out the source section if you want it to run faster.

# One thing I could improve would be to detect each branch. However, since the "post" variable in example.py assumes the main branch, I will do the same for the source data (with an extra check for the master branch)

post = '/raw/main/README.md'

extU = URLExtract()
DOIpattern = r'10.\d{4,9}/[-._;()/:A-Z0-9]+' #From internet
BIBpattern = r'@[\w]+\{[^}]+\}' #From internet

post = '/raw/main/README.md'
postGH = '/refs/heads/main/README.md'
postGH2 = '/refs/heads/master/README.md'


source_ids = []

def extractURLs (c):
 res = extU.find_urls (c)
 return res

def extractDOIs (c):
 res = re.findall (DOIpattern, c, re.IGNORECASE)
 return res

def extractBIBs (c):
 res = re.findall(BIBpattern, c, re.IGNORECASE)
 return res

fo = gzip.open(f"output/{utid}.json.gz", 'w')

def run (tp):
   with open(f"input/{utid}_{tp}", 'r') as f:
      for line in f:

         line = line.strip ()
         if tp == 'source':
            _, line = line.split(';') #We don't need the first part of the line
            #Get everything after the gh/ part
            line = line[11:]
         # print(line)
         url = base[tp] + f"{line}{post}" if tp != 'source' else base[tp] + f"{line}{postGH}"
         print(url)
         try:
            r = requests.get (url)
            content = r.text

            #strip newlines from content as requested in writeup
            content = content.replace('\n', ' ').replace('"', "\"").replace("'", "\'").replace('\t', ' ').replace('\r', ' ')
            urls = extractURLs(content)
            dois = extractDOIs(content)
            bibs = extractBIBs(content)

            # Tries "main" and "master" branches if "main" branch is not found
            if content in ["404: Not Found"]:
               print("Main branch not found, trying master branch")
               url = base[tp] + f"{line}{post}" if tp != 'source' else base[tp] + f"{line}{postGH2}"
               print(url)
               r = requests.get (url)
               content = r.text
               if content == "404: Not Found":
                  print("Master branch not found")
                  content = "No README found"

            #Tells if nothing is found
            if len(urls) == 0:
               urls = "No URLs found"
            if len(dois) == 0:
               dois = "No DOIs found"
            if len(bibs) == 0:
               bibs = "No BIBs found"

            #Given (According to prof, no need to change this)
            res = { 'ID': line, 'type': tp, 'url': url, 'content': content, 'links': urls, 'dois': dois, 'bibs': bibs }
            out = json.dumps(res, ensure_ascii=False)
            fo.write((out+"\n").encode('utf-8'))
         except Exception as e:
            #Write something, anyway
            print(f"Error in processing {url}: {e}")
            res = { 'ID': line, 'type': tp, 'url': url, 'content': "None - error in reading URL", 'links': "No URLs Found", 'dois': "No DOI's Found", 'bibs': "No BIB's Found" }
            out = json.dumps(res, ensure_ascii=False)
            fo.write((out+"\n").encode('utf-8'))

run('model')
run('data')
run('source')

fo.close()


#debug code to extract the gzip file
# with gzip.open(f"output/{utid}.json.gz", 'rb') as f:
#    file_content = f.read()
#    with open(f"output/{utid}.json", 'wb') as f_out:
#       f_out.write(file_content)