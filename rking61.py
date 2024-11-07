import json, re
import requests
from urlextract import URLExtract
import sys, gzip


utid = "rking61"
base = {
    "model": "https://huggingface.co/",
    "data": "https://huggingface.co/datasets/",
    "source": "https://",
}
post = "/raw/main/README.md"
postGH_master = "blob/master/README.md"  # or it could be 'blob/main/README.md'
postGH_main = "blob/main/README.md"

extU = URLExtract()
DOIpattern = r"\b(10\.\d{4,9}\/[-._;()/:A-Z0-9]+)\b/i"  # r1\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?!["&\'<>])[[:graph:]])+)\b'
BIBpattern = r"@\w+\{[^}]+\}"


def extractURLs(c):
    res = extU.find_urls(c)
    return res


def extractDOIs(c):
    res = re.findall(DOIpattern, c)
    return res


def extractBIBs(c):
    res = re.findall(BIBpattern, c, re.DOTALL)
    return res


fo = gzip.open(f"output/{utid}.json.gz", "w")


def run(tp):
    post0 = post
    with open(f"input/{utid}_{tp}", "r") as f:
        for line in f:
            line = line.strip()
            if tp == "source":
                (npapers, line) = line.split(";")
                post0 = postGH_master
            print(line)
            url = base[tp] + f"{line}{post0}"

            # Two of my github urls were not valid, so I make them valid here
            if "github:com" in url or "github com" in url:
                url = url.replace(url, "https://github.com")

            r = requests.get(url)
            content = r.text
            # github returns repos that do not exist, need to detect that here
            # github when you give master instead of main, that might cause issues as well
            if r.status_code == 404:
                if tp == "source":
                    url = base[tp] + f"{line}{postGH_main}"
                    r = requests.get(url)
                    if r.status_code == 404:
                        continue
                else:
                    continue
            urls = extractURLs(content)
            dois = extractDOIs(content)
            bibs = extractBIBs(content)
            res = {
                "ID": line,
                "type": tp,
                "url": url,
                "content": content,
                "links": urls,
                "dois": dois,
                "bibs": bibs,
            }
            out = json.dumps(res, ensure_ascii=False)
            fo.write((out + "\n").encode())


run("model")
run("data")
run("source")
