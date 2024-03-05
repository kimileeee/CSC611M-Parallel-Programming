# CSC611M-Parallel-Programming

## Overview

This Python program is designed to scrape email addresses from web pages of a particular site within a set time frame. It navigates through web pages starting from a given URL, collects all unique email addresses found, and saves them along with associated names. It implements multiprocessing to facilitate the optimization of the web scraping process.

## Dependencies

To run this program, you will need Python 3 and the following Python libraries:

* `requests` for making HTTP requests
* `BeautifulSoup` from `bs4` for parsing HTML content
* `multiprocessing` for concurrent execution
* `re` for regular expression operations

These dependencies can be installed using pip (Python's package installer). If you do not have pip installed, you will need to install it first. Once pip is installed, you can install the required libraries using the following command:

```
pip install requests beautifulsoup4
```

How to Run

1. Ensure all dependencies are installed.
2. Open a terminal or command prompt.
3. Navigate to the directory containing the script.
4. Run the script using Python:

```
python csc611m_scraper.py
```

## Input

* **Starting URL** : The program is currently set to start scraping from "[https://www.dlsu.edu.ph](https://www.dlsu.edu.ph/)", but this can be changed within the code.
* **Duration** : The duration of the web scraping activity in minutes.
* **Link Scraper Count** : The number of processes allocated for scraping links.
* **Info Scraper Count** : The number of processes allocated for scraping email information.

## Output

* A CSV file named `EmailData_TIMESTAMP.csv` containing the names and email addresses collected.
* A TXT file named `ScrapingStats_TIMESTAMP.txt` with statistics about the scraping session.

## Contributors

This project is in partial fulfillment of the course CSC611M for Term 2, A.Y. 2023 - 2024. Listed below are the contributors to this project:

* [Ralph Angelo Furigay](https://github.com/Rafu-00)
* [Kim Williame Lee](https://github.com/kimileeee)
