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

<pre><div class="dark bg-gray-950 rounded-md"><div class="flex items-center relative text-token-text-secondary bg-token-main-surface-secondary px-4 py-2 text-xs font-sans justify-between rounded-t-md"><span>bash</span><span class="" data-state="closed"><button class="flex gap-1 items-center"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="icon-sm"><path fill-rule="evenodd" clip-rule="evenodd" d="M12 4C10.8954 4 10 4.89543 10 6H14C14 4.89543 13.1046 4 12 4ZM8.53513 4C9.22675 2.8044 10.5194 2 12 2C13.4806 2 14.7733 2.8044 15.4649 4H17C18.6569 4 20 5.34315 20 7V19C20 20.6569 18.6569 22 17 22H7C5.34315 22 4 20.6569 4 19V7C4 5.34315 5.34315 4 7 4H8.53513ZM8 6H7C6.44772 6 6 6.44772 6 7V19C6 19.5523 6.44772 20 7 20H17C17.5523 20 18 19.5523 18 19V7C18 6.44772 17.5523 6 17 6H16C16 7.10457 15.1046 8 14 8H10C8.89543 8 8 7.10457 8 6Z" fill="currentColor"></path></svg>Copy code</button></span></div><div class="p-4 overflow-y-auto"><code class="!whitespace-pre hljs language-bash">pip install requests beautifulsoup4
</code></div></div></pre>

## How to Run

1. Ensure all dependencies are installed.
2. Open a terminal or command prompt.
3. Navigate to the directory containing the script.
4. Run the script using Python:

<pre><div class="dark bg-gray-950 rounded-md"><div class="flex items-center relative text-token-text-secondary bg-token-main-surface-secondary px-4 py-2 text-xs font-sans justify-between rounded-t-md"><span>bash</span><span class="" data-state="closed"><button class="flex gap-1 items-center"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="icon-sm"><path fill-rule="evenodd" clip-rule="evenodd" d="M12 4C10.8954 4 10 4.89543 10 6H14C14 4.89543 13.1046 4 12 4ZM8.53513 4C9.22675 2.8044 10.5194 2 12 2C13.4806 2 14.7733 2.8044 15.4649 4H17C18.6569 4 20 5.34315 20 7V19C20 20.6569 18.6569 22 17 22H7C5.34315 22 4 20.6569 4 19V7C4 5.34315 5.34315 4 7 4H8.53513ZM8 6H7C6.44772 6 6 6.44772 6 7V19C6 19.5523 6.44772 20 7 20H17C17.5523 20 18 19.5523 18 19V7C18 6.44772 17.5523 6 17 6H16C16 7.10457 15.1046 8 14 8H10C8.89543 8 8 7.10457 8 6Z" fill="currentColor"></path></svg>Copy code</button></span></div><div class="p-4 overflow-y-auto"><code class="!whitespace-pre hljs language-bash">python csc611m_scraper.py
</code></div></div></pre>

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
