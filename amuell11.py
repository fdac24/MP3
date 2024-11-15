"""
    name: Andrew Mueller
    netid: amuell11
    assignement: 

        # Scrape and store model and data readme files for scientific domains

        You have  approximately 75 models and 105 datasets hosted on
        HuggingFace Hub in your netid_model and netid_data
        files.
        In addition, you have a sample of github repositories mentioned in
        scientific papers.

        For each please scrape and store the content of the readme files
        For each retrieved README file extract all URLs and DOI's in it. For
        bonus points extract bib entries as well. 
        Store the results in a (compressed) json file containing a
        dictionary with the following keys:

        1. 'id': e.g., 'LoneStriker/SauerkrautLM-Mixtral-8x7B-3.0bpw-h6-exl2'
        1. 'type': '(data|model|source)'
        1. 'url':
            e.g. 'https://huggingface.co/datasets/pankajmathur/alpaca_orca/raw/main/README.md'
            or 'https://huggingface.co/iamacaru/climate/raw/main/README.md'
        1. 'content': "the content of the readme file" - no newlines
        1. 'links': [ an array of extracted URLs ]
        1. 'dois': [ an array of extracted DOIs ]
        1. 'bibs': [ an array of extracted bib entries ] - bonus points

        Each line is separately json encoded. Output should be in a single file output/netid.json.gz
        and your source code will be in netid.py (or netid.ipynb if you
        prefer to use collab notebooks).

        See example in example.py.

        Happy scraping! 

"""
import re
import aiohttp
import time
import asyncio
import logging
import concurrent.futures
from typing import Dict, List, Tuple
import json
from urlextract import URLExtract
from concurrent.futures import ThreadPoolExecutor
from unidecode import unidecode
import chardet
import gzip

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

input_path = "input/"
net_id = "amuell11"

readme_pattern = re.compile(r'"name"\s*:\s*"readme(?:\.[\w\.\-]+)?"', flags=re.IGNORECASE)
branch_pattern = re.compile(r'"defaultBranch"\s*:\s*"([^"]+)"', flags=re.IGNORECASE)
doi_pattern = re.compile(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+")
bibtex_pattern = re.compile(r"@[\w]+\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", flags=re.DOTALL)

def process_gh_response(response_text: str, url: str) -> str:
    """
    Processes a GitHub repository's page response to construct a URL to its raw README file.

    This function extracts the README file name and the default branch name from the provided
    GitHub repository page's response text using precompiled regular expressions. It then constructs
    a URL pointing to the raw content of the README file in the default branch of the repository.

    Args:
        response_text (str): The HTML or JSON content of the GitHub repository page.
        url (str): The original URL of the GitHub repository page.

    Returns:
        str: A URL pointing to the raw README file in the default branch of the repository.
             If the README or default branch is not found, returns the original URL.

    """

    if response_text is None:
        return url
    
    # Extract readme and default branch information
    search = readme_pattern.findall(response_text)
    if len(search) == 0:
        logger.warning(f"No README found for {url}")
        return url
    
    readme_file = search[0].split(":\"")[1].split("\"")[0]

    search = branch_pattern.findall(response_text)
    if len(search) == 0:
        logger.warning(f"No branch information found for {url}")
        return url
    branch_name = search[0]

    return url + "/raw/" + branch_name + "/" + readme_file

async def fetch(semaphore: asyncio.Semaphore, session: aiohttp.ClientSession, url: str) -> Tuple[str, str | None, int]:
    """
    Asynchronously fetches content from a given URL with rate limiting and encoding handling.

    This function performs an HTTP GET request to the specified URL within the context of an asyncio
    semaphore to limit concurrency. It handles HTTP status codes, specifically retrying on rate limits
    (HTTP 429). Upon receiving a successful response, it attempts to read the text content, handling
    potential Unicode decoding errors by detecting the appropriate encoding and decoding accordingly.
    Non-ASCII characters are transliterated using `unidecode`.

    Args:
        semaphore (asyncio.Semaphore): A semaphore to control the number of concurrent requests.
        session (aiohttp.ClientSession): An aiohttp client session for making HTTP requests.
        url (str): The URL to fetch content from.

    Returns:
        tuple:
            - url (str): The URL that was fetched.
            - text (str or None): The decoded text content of the response, or None if unsuccessful.
            - status_code (int): The HTTP status code of the response.

    """
    sleep_time = 5.0
    async with semaphore:
        while True:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        logger.info(f"Successfully fetched {url} with 200 status")
                        text = ""
                        try:
                            text = await response.text()
                        except UnicodeDecodeError:
                            raw_content = await response.read()
                            detected_encoding = chardet.detect(raw_content)['encoding']
                            text_content = raw_content.decode(detected_encoding or 'utf-8', errors='replace')
                            text_content_clean = unidecode(text_content)
                            text = text_content_clean

                        return url, text, 200
                    elif response.status == 429:
                        logger.warning(f"Rate limit hit for {url}; Retrying after {sleep_time} second delay.")
                        await asyncio.sleep(sleep_time)
                    else:
                        logger.error(f"{response.status} error for {url}")
                        return url, None, response.status
                    
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.error(f"Exception occurred while fetching {url}: {e}, retrying!")

async def process_repos_async(type: str = "") -> List[Tuple[str, str, str, str, int]]:
    """
    Asynchronously processes a list of repositories based on the specified type and fetches their README files.

    This function reads repository identifiers from an input file and constructs URLs to their README files.
    It then uses asynchronous I/O to fetch the content of these README files concurrently.
    For repositories of type 'source', it performs additional processing to handle GitHub repositories,
    using the `process_gh_response` function to extract the correct raw README URLs.

    Args:
        type (str): The type of repositories to process. Must be one of 'data', 'model', or 'source'.

    Returns:
        List[Tuple[str, str, str, str, int]]: A list of tuples, each containing:
            - type (str): The repository type provided as input.
            - base_url (str): The base identifier or URL of the repository.
            - fetched_url (str): The URL from which the README was fetched.
            - content (str): The content of the README file.
            - response_code (int): The HTTP status code from the fetch operation.
    """
    file = input_path + net_id + "_" + type
    semaphore = asyncio.Semaphore(15) 
    source_results = []
    full_urls = []
    tasks = []
    num_ok_responses = 0
    base_urls = []

    with open(file, "r") as f:
        
        base_urls = [x.strip("\n") for x in f.readlines()]

        if type == "data":
            full_urls = ["https://huggingface.co/datasets/" + x + "/raw/main/README.md" for x in base_urls]
        elif type == "model":
            full_urls = ["https://huggingface.co/" + x + "/raw/main/README.md" for x in base_urls]
        elif type == "source":
            base_urls = [x.split(";")[1] for x in base_urls]
            full_urls = ["https://" + x for x in base_urls]
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
                    if response_code == 200:
                        num_ok_responses += 1
                    future = loop.run_in_executor(executor, process_gh_response, response_text, url)
                    further_tasks.append(future)

                source_results = await asyncio.gather(*further_tasks)

            tasks = []
            
            for url in source_results:

                tasks.append(fetch(semaphore, session, url))

            responses = await asyncio.gather(*tasks)

            print(f"Num valid readme files: {num_ok_responses}")

        return_list = []

        for base, full in zip (base_urls, responses):
            if base == full[0]:
                continue
            return_list.append((type, base, full[0], full[1], full[2]))

        return return_list

def process_single_entry(data: Tuple[str, str, str, str, int]) -> Dict | None:
    """
    Processes a single data entry to extract links, DOIs, and BibTeX entries.

    This function takes a tuple containing information about a resource (e.g., a repository or dataset)
    and processes the text content to extract URLs, DOIs, and BibTeX entries. It returns a dictionary
    containing the extracted information or None if the response code indicates a failed fetch.

    Args:
        data (Tuple[str, str, str, str, int]):
            - type (str): The type of the resource (e.g., 'data', 'model', 'source').
            - base_url (str): The base identifier or URL of the resource.
            - full_url (str): The full URL from which the content was fetched.
            - text (str): The text content retrieved from the resource.
            - response_code (int): The HTTP status code from the fetch operation.

    Returns:
        Dict | None:
            - A dictionary with the following keys:
                - 'id' (str): The base identifier or URL of the resource.
                - 'type' (str): The type of the resource.
                - 'url' (str): The full URL from which the content was fetched.
                - 'content' (str): The text content with newlines removed.
                - 'links' (List[str]): A list of unique URLs extracted from the content.
                - 'dois' (List[str]): A list of DOIs extracted from the content.
                - 'bibs' (List[str]): A list of BibTeX entries extracted from the content with newlines removed.
            - Returns None if the response code is not 200.
    """
    type, base_url, full_url, text, response_code = data
    
    if response_code != 200:
        return None
    
    if ("https://" + base_url) == full_url:
        return None
    
    if text is None:
        return None
    
    extU = URLExtract()

    links = extU.find_urls(text, only_unique=True)
    dois = doi_pattern.findall(text)
    bibtexs = [re.sub("\n", "", x) for x in bibtex_pattern.findall(text)]
    
    logger.info(f"Finished processing {full_url}")

    return {
        "id": base_url,
        "type": type,
        "url": full_url,
        "content": re.sub("\n", "", text),
        "links": links,
        "dois": dois,
        "bibs": bibtexs
    }

def process_readme_files(data_responses: List[Tuple[str, str, str, str, int]]) -> List[Dict]:
    """
    Processes a list of README file data responses concurrently to extract relevant information.

    This function utilizes a thread pool executor to process multiple README files in parallel.
    Each data response is a tuple containing information about a resource, and the function
    applies `process_single_entry` to each entry to extract links, DOIs, BibTeX entries,
    and other relevant data.

    Args:
        data_responses (List[Tuple[str, str, str, str, int]]):
            A list of tuples, each containing:
                - type (str): The type of the resource (e.g., 'data', 'model', 'source').
                - base_url (str): The base identifier or URL of the resource.
                - full_url (str): The full URL from which the README was fetched.
                - text (str): The content of the README file.
                - response_code (int): The HTTP status code from the fetch operation.

    Returns:
        List[Dict]:
            A list of dictionaries containing the processed data from each README file.
            Each dictionary includes:
                - 'id' (str): The base identifier or URL of the resource.
                - 'type' (str): The type of the resource.
                - 'url' (str): The full URL from which the content was fetched.
                - 'content' (str): The processed text content with newlines removed.
                - 'links' (List[str]): A list of extracted URLs from the content.
                - 'dois' (List[str]): A list of extracted DOIs from the content.
                - 'bibs' (List[str]): A list of extracted BibTeX entries from the content.
    """
    parsed_data = []

    with ThreadPoolExecutor(max_workers=16) as executor:
        results = executor.map(process_single_entry, data_responses)

    parsed_data.extend(result for result in results if result is not None)

    return parsed_data

if __name__ == "__main__":

    start_time = time.time()

    # Run for each type asynchronously
    loop = asyncio.get_event_loop()

    
    s = time.time()
    data_responses = loop.run_until_complete(process_repos_async("data"))
    e = time.time()
    print("Time to process data urls:", e-s)


    s = time.time()
    model_responses = loop.run_until_complete(process_repos_async("model"))
    e = time.time()
    print("Time to process model urls:", e-s)
    

    s = time.time()
    source_responses = loop.run_until_complete(process_repos_async("source"))
    e = time.time()
    print("Time to process source:", e-s)


    readme_info = data_responses + model_responses + source_responses
    s = time.time()
    parsed_data = process_readme_files(readme_info)
    e = time.time()
    print(f"Time to proccess README's: {e - s}")

    end_time = time.time()

    with gzip.open("output/amuell11.json.gz", "w") as f:
        for entry in parsed_data:
            f.write((json.dumps(entry, ensure_ascii=False) + "\n").encode())

    print(len(parsed_data))

    print(f"Total time: {(end_time - start_time) / 60} minutes")
