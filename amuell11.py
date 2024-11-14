import re
import aiohttp
import time
import asyncio
import logging
import concurrent.futures
from typing import Dict
import json

# Configure logging
# logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

input_path = "input/"
net_id = "amuell11"

def process_gh_response(response_text, url):
    
    if url is None:
        print("Fatal error, URL can not be None!")
        exit(1)
    
    if response_text is None:
        return url
    
    # Extract readme and default branch information
    readme_pattern = r'"name"\s*:\s*"readme(?:\.[\w\.\-]+)?"'
    search = re.findall(readme_pattern, response_text, flags=re.IGNORECASE)
    if len(search) == 0:
        logger.warning(f"No README found for {url}")
        return url
    readme_file = search[0].split(":\"")[1].split("\"")[0]

    branch_pattern = r'"defaultBranch"\s*:\s*"([^"]+)"'
    search = re.findall(branch_pattern, response_text, flags=re.IGNORECASE)
    if len(search) == 0:
        logger.warning(f"No branch information found for {url}")
        return url
    branch_name = search[0]

    return url + "/blob/" + branch_name + "/" + readme_file

async def fetch(semaphore, session, url):
    async with semaphore:
        while True:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        return url, await response.text(), 200
                    elif response.status == 429:
                        logger.warning(f"Rate limit hit for {url} Retrying after delay...")
                        await asyncio.sleep(5.0)
                    else:
                        logger.warning(f"Non-200 response for {url}: {response.status}")
                        return url, None, 404
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.error(f"Exception occurred while fetching {url}: {e}, retrying!")

async def process_repos_async(type: str = "") -> list[(str, str, int)]:
    
    file = input_path + net_id + "_" + type
    semaphore = asyncio.Semaphore(10) 
    source_results = []
    full_urls = []
    tasks = []
    
    with open(file, "r") as f:
        if type == "data":
            full_urls = ["https://huggingface.co/datasets/" + x.strip("\n") + "/blob/main/README.md" for x in f.readlines()]
        elif type == "model":
            full_urls = ["https://huggingface.co/" + x.strip("\n") + "/blob/main/README.md" for x in f.readlines()]
        elif type == "source":
            full_urls = ["https://" + x.strip("\n").split(";")[1] for x in f.readlines()]
        else: 
            raise ValueError("Not a valid type entered")
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:

        for url in full_urls:
            tasks.append(fetch(semaphore, session, url))

        responses = await asyncio.gather(*tasks)
        
        if type == "source":
            with concurrent.futures.ThreadPoolExecutor() as executor:
                loop = asyncio.get_running_loop()
                further_tasks = []

                for idx, response in enumerate(responses):
                    url, response_text, response_code = response
                    
                    future = loop.run_in_executor(executor, process_gh_response, response_text, url)
                    further_tasks.append(future)
                    
                    # if response_code != 200:
                        
                    # else:
                    #     further_tasks.append(future)

                source_results = await asyncio.gather(*further_tasks)
                
                # for task, is_success in further_tasks:
                #     result = await task
                #     source_results.append(result)
                    # if is_success is True:
                        
                    # else:
                    #     source_results.append(result)
            tasks = []
            
            for url in source_results:
                tasks.append(fetch(semaphore, session, url))

            responses = await asyncio.gather(*tasks)
        
        return responses
    
if __name__ == "__main__":
    # Run for each type asynchronously
    loop = asyncio.get_event_loop()
    s = time.time()
    data_responeses = loop.run_until_complete(process_repos_async("data"))
    # print(result)
    e = time.time()
    print("Time to process data:", e-s)
    s = time.time()
    model_responses = loop.run_until_complete(process_repos_async("model"))
    e = time.time()
    print("Time to process model:", e-s)
    s = time.time()
    source_responses = loop.run_until_complete(process_repos_async("source"))
    e = time.time()
    print("Time to process source:", e-s)
    print(len(source_responses))
    with open("test.txt", "w") as f:
        json.dump(source_responses, f)