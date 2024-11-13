# Scrape and store model and data readme files for  scientific domains

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
