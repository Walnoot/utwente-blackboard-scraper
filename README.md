# utwente-blackboard-scraper
A simple tool to scrape lecture slides of the University of Twente Blackboard site before it goes down

## Requirements

- python3
- Selenium Chrome WebDriver and python3 language bindings ([docs](https://www.selenium.dev/documentation/en/selenium_installation/))
- wget

## Usage

> python3 scrape.py

## Output

All scraped files can be found in the `output` directory, and are sorted on course name and Blackboard directory structure. By default, only PDF and Microsoft Word/PowerPoint files are scraped. 

## Configuration

None. Edit the python script to suit your needs.
