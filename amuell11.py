import requests
import re
import json
import gzip
from typing import List, Dict, Optional

net_id = "amuell11"
input_path = "input/"
data_type = ["data", "model", "source"]



def fetch_hf_readme(repo_id: str) -> Optional[str]:
    """Fetch the README.md content from a Hugging Face repository."""
    url = f"https://huggingface.co/{repo_id}/raw/main/README.md"
    response = requests.get(url)
    if response.status_code == 200:
        print(response.text)
        return response.text
    else:
        print(f"Failed to fetch README for {repo_id} from Hugging Face.")
        return None

def extract_urls(text: str) -> List[str]:
    pass

def extract_dois(text: str) -> List[str]:
    pass

def extract_bibtex_entries(text: str) -> List[str]:
    pass

def process_repos(type: str = "") -> Dict:

    file = input_path + net_id + "_" + type
    full_urls = []
    with open(file, "r") as f:
        if type == "data":
            full_urls = ["https://huggingface.co/datasets/" 
                                + x.strip("\n") + 
                                "/blob/main/README.md" 
                                for x in f.readlines()]
        elif type == "model":
            full_urls = ["https://huggingface.co/" 
                                + x.strip("\n") + 
                                "/blob/main/README.md" 
                                for x in f.readlines()]
        elif type == "source":
            full_urls = ["https://" 
                                + x.strip("\n").split(";")[1] \
                                for x in f.readlines()]
        else:
            raise ValueError("Not a valid type entered")
    
    reponse_not_ok_count = 0
    readme_not_found_count = 0
    
    readme_pattern = re.compile(r'"name"\s*:\s*"readme(?:\.[\w\.\-]+)?"', flags= re.IGNORECASE)
    branch_pattern = re.compile(r'"defaultBranch"\s*:\s*"([^"]+)"', flags = re.IGNORECASE)
    
    for idx, url in enumerate(full_urls):
        response = requests.get(url)
        
        if response.status_code == 200:
            
            # In order to maximize the number of readme files we can grab on to
            #   we will look at the entire repo and find the readme file extension, 
            #   as well as the name of the parent branch, i.e. "main", "master", or whatever else it
            #   can be listed as. 
            if type == "source":
                # readme_pattern = r'"name"\s*:\s*"readme(?:\.[\w\.\-]+)?"'
                search = readme_pattern.findall(response.text)
                # re.findall(readme_pattern, response.text, flags=re.IGNORECASE)
                if len(search) == 0:
                    readme_not_found_count += 1
                    continue
                readme_file = search[0].split(":\"")[1].split("\"")[0]
                
                search = branch_pattern.findall(response.text)
                if len(search) == 0:
                    print("fatal error!", url)
                    exit(0)
                    continue

                branch_name = search[0]
                readme_url = url + "/blob/" + branch_name + "/" + readme_file 
                
                readme_response = requests.get(readme_url)
                if readme_response.status_code == 200:
                    print(idx, ":", readme_url)
                else:
                    print(idx, ":", readme_url)
                    reponse_not_ok_count += 1
        else:
            reponse_not_ok_count += 1
            continue

    print(reponse_not_ok_count)
        
if __name__ == "__main__":
    # process_repos("data")
    # process_repos("model")
    process_repos("source")
    
# import re
# import aiohttp
# import time
# import asyncio
# from typing import Dict

# input_path = "input/"
# net_id = "amuell11"

# async def fetch(session, url):
#     try:
#         async with session.get(url) as response:
#             if response.status == 200:
#                 return url, await response.text()
#             else:
#                 return url, None
#     except Exception as e:
#         return url, None

# async def process_repos_async(type: str = "") -> Dict:
#     file = input_path + net_id + "_" + type
#     full_urls = []
    
#     with open(file, "r") as f:
#         if type == "data":
#             full_urls = ["https://huggingface.co/datasets/" + x.strip("\n") + "/blob/main/README.md" for x in f.readlines()]
#         elif type == "model":
#             full_urls = ["https://huggingface.co/" + x.strip("\n") + "/blob/main/README.md" for x in f.readlines()]
#         elif type == "source":
#             full_urls = ["https://" + x.strip("\n").split(";")[1] for x in f.readlines()]
#         else:
#             raise ValueError("Not a valid type entered")

#     response_not_ok_count = 0
#     readme_response_not_ok = 0
#     repo_response_not_ok = 0
#     no_readme_count = 0
#     tasks = []

#     async with aiohttp.ClientSession() as session:
#         for url in full_urls:
#             tasks.append(fetch(session, url))

#         responses = await asyncio.gather(*tasks)

#         for idx, (url, response_text) in enumerate(responses):
#             if not response_text:
#                 response_not_ok_count += 1
#                 print(url)
#                 continue

#             if type == "source":
#                 # Extract readme and default branch information
#                 readme_pattern = r'"name"\s*:\s*"readme(?:\.[\w\.\-]+)?"'
#                 search = re.findall(readme_pattern, response_text, flags=re.IGNORECASE)
#                 if len(search) == 0:
#                     no_readme_count += 1
#                     continue
#                 readme_file = search[0].split(":\"")[1].split("\"")[0]

#                 branch_pattern = r'"defaultBranch"\s*:\s*"([^"]+)"'
#                 search = re.findall(branch_pattern, response_text, flags=re.IGNORECASE)
#                 if len(search) == 0:
#                     continue
#                 branch_name = search[0]

#                 readme_url = url + "/blob/" + branch_name + "/" + readme_file
#                 async with session.get(readme_url) as readme_response:
#                     if readme_response.status == 200:
#                         print(idx, ":", readme_url)
#                     else:
#                         readme_response_not_ok += 1
#             else:
#                 # print(idx, ":", url)
#                 pass

#     print("Total non-200 responses:", response_not_ok_count)

# if __name__ == "__main__":
#     # Run for each type asynchronously
#     loop = asyncio.get_event_loop()
#     s = time.time()
#     loop.run_until_complete(process_repos_async("data"))
#     e = time.time()
#     print("Time to process data:", e-s)
#     s = time.time()
#     loop.run_until_complete(process_repos_async("model"))
#     e = time.time()
#     print("Time to process model:", e-s)
#     s = time.time()
#     loop.run_until_complete(process_repos_async("source"))
#     e = time.time()
#     print("Time to process source:", e-s)
