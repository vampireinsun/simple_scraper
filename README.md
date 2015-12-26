# simple_scraper
a simple implementation for scraping some content from a testing page
files structure
---------------------
1. scraper.py: the main body for the implementaiton.
2. test.py: the module containing all the unit tests
3. utils.py: some shared functions. 
4. ./fixtures/*.*: The txt or json files used in unit tests.

Usage
-----------------------
1. Scrape the content from the testing page
The help:
>python ./scraper.py -h
The example of command line for runing this script
>python ./scraper.py -o ./data.json

2. Run the unit tests
>python ./test.py
