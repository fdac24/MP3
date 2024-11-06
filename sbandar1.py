import json, re
import requests
import gzip

netid = "sbandar1"
base_urls = {
  "model": "https://huggingface.co/",
  "data": "https://huggingface.co/datasets/",
  "source": "https://"
}

post_urls = {
  "hugging_face": "/raw/main/README.md",
  "github_master": "/blob/master/README.md",
  "github_main": "/blob/main/README.md"
}

input_files = ["model", "data", "source"]

regex = {
  "url": r"https?://[^\s,]+",
  "doi": r"\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)\b",
  "bib": r"@[^}]+}"
}

output = gzip.open(f"output/{netid}.json.gz", "w", compresslevel=9)

def run(file):
  with open(f"input/{netid}_{file}", "r", encoding="utf-8") as f:
    for line in f:
      links = []

      line = line.strip()
      base = base_urls[file]

      if file == "source":
        _, line = line.split(";")

        if not re.search(r"github\.com", line):
          line = re.sub(r"github\s*com", "github.com", line)
        
        links.append(base + line + post_urls["github_main"])
        links.append(base + line + post_urls["github_master"])
      else:
        links.append(base + line + post_urls["hugging_face"])
      
      for link in links:
        content = requests.get(link)
        if content.status_code == 404:
          continue
        else: 
          content = content.text

        urls = re.findall(regex["url"], content, re.IGNORECASE)
        dois = re.findall(regex["doi"], content, re.IGNORECASE)
        bibs = re.findall(regex["bib"], content, re.IGNORECASE)

        json_obj = {
          "id": line,
          "type": file,
          "url": link,
          "content": content,
          "links": urls,
          "dois": dois,
          "bibs": bibs
        }

        json_obj = json.dumps(json_obj, ensure_ascii=False)
        output.write((json_obj + "\n").encode())
        break

if __name__ == "__main__":
  for file in input_files:
    run(file)
  output.close()
