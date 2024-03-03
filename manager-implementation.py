import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from multiprocessing import Process, Manager
import time
import re

def cfDecodeEmail(encodedString):
    r = int(encodedString[:2],16)
    email = ''.join([chr(int(encodedString[i:i+2], 16) ^ r) for i in range(2, len(encodedString), 2)])
    return email

def all_unique(lis):
    return len(set(lis)) == len(lis)

def getLinks(url):
    response = requests.get(url=url)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find_all('a', href=True)

    base_url = "https://www.dlsu.edu.ph"
    pattern = re.compile(r'\.\w+$')
    found_links = []

    for link in links:
        linkToScrape = urljoin(base_url, link['href'])
        if 'href' in link.attrs:
            if pattern.search(link['href']) or linkToScrape.startswith("https://www.dlsu.edu.ph/cdn-cgi/l/email-protection#"):
                continue
            else:
                found_links.append(linkToScrape)
        else:
            continue

    return found_links

def extractEmailsFromPage(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    encoded_emails = soup.find_all('a', {"class": "__cf_email__"})
    unprotected_emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', soup.get_text())
    collected_emails = []
    
    for i in range(len(encoded_emails)):
        encoded = encoded_emails[i]['data-cfemail']
        decoded = cfDecodeEmail(encoded)
        collected_emails.append(decoded)

    collected_emails.extend(unprotected_emails)

    if len(collected_emails) != 0:
        print(f"Email addresses collected from {url}: {collected_emails}")

    return collected_emails

def extractEmailsFromLinks(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find_all('a')
    emails = []

    for link in links:
        if 'href' in link.attrs:
            if link['href'].find("/cdn-cgi/l/email-protection#") == -1:
                continue
            else:
                encoded = link['href'].removeprefix("https://www.dlsu.edu.ph/cdn-cgi/l/email-protection#")
                decoded = cfDecodeEmail(encoded)
                emails.append(decoded)
        else:
            continue

    if len(emails) != 0:
        print(f"Email address collected from links within {url}: {emails}")
        
    return emails

class LinkScraper(Process):
    def __init__(self, ID, starting_point, url_list, visited_list, completed_list, start_time, duration):
        Process.__init__(self)
        self.ID = ID
        self.starting_point = starting_point
        self.url_list = url_list
        self.visited_list = visited_list
        self.completed_list = completed_list
        self.start_time = start_time
        self.duration = duration
    def run(self):
        self.url_list.append(self.starting_point)

        while self.url_list and time.time() - self.start_time <= self.duration * 60:
            print("LinkScraper running")
            curr_url = self.url_list.pop(0)

            if curr_url in self.visited_list or curr_url in self.url_list or curr_url in self.completed_list:
                continue

            self.visited_list.append(curr_url)

            try:
                found_links = getLinks(curr_url)

                for link in found_links:
                    if link not in self.visited_list and link not in self.completed_list and link not in self.url_list and "https://www.dlsu.edu.ph/" in link:
                        self.url_list.append(link)
                        print(f"LinkScraper {self.ID} added {link}")

            except:
                print("Error encountered, info scraping skipped")
                continue

class InfoScraper(Process):
    def __init__(self, ID, visited_list, completed_list, info_list, start_time, duration):
        Process.__init__(self)
        self.ID = ID
        self.visited_list = visited_list
        self.completed_list = completed_list
        self.info_list = info_list
        self.start_time = start_time
        self.duration = duration
    def run(self):

        while self.visited_list and time.time() - self.start_time <= self.duration * 60:
            print(f"InfoScraper {self.ID} running")
            curr_link = self.visited_list.pop(0)
            self.completed_list.append(curr_link)

            try:
                scraped_emails = extractEmailsFromPage(curr_link)
                scraped_emails.extend(extractEmailsFromLinks(curr_link))

                for email in scraped_emails:
                    if email not in self.info_list:
                        self.info_list.append(email)
                        print(f"InfoScraper {self.ID} found something - current email list: {self.info_list}")
                    
            except:
                continue
        
        print(f"InfoScraper {self.ID} has finished scraping")

if __name__ == "__main__":
    # starting_url = input("Enter starting point for web scraping:\n")
    starting_url = "https://www.dlsu.edu.ph"

    duration = input("Enter web scraping duration (in minutes):\n")
    duration = int(duration)

    link_scraper_count = input("Enter number of processes to allocate for link scraping:\n")
    link_scraper_count = int(link_scraper_count)

    info_scraper_count = input("Enter number of processes to allocate for info scraping: \n")
    info_scraper_count = int(info_scraper_count)

    manager = Manager()
    url_list = manager.list()
    visited_list = manager.list()
    completed_list = manager.list()
    info_list = manager.list()
    processes = []
    
    start_time = time.time()

    for i in range(link_scraper_count):
        link_scraper = LinkScraper(i, starting_url, url_list, visited_list, completed_list, start_time, duration)
        link_scraper.start()
        processes.append(link_scraper)
    
    print("Sleeping for 5 seconds to initiate link scraper")
    time.sleep(5)

    for i in range(info_scraper_count):
        info_scraper = InfoScraper(i, visited_list, completed_list, info_list, start_time, duration)
        info_scraper.start()
        processes.append(info_scraper)

    for p in processes:
        p.join()

    end_time = time.time()
    execution_time = end_time - start_time

    print(f"Execution time: {execution_time:2.2f}")

    print(f"Number of pages scraped: {len(completed_list)}")
    print(f"Were all pages scraped unique? {all_unique(completed_list)}")
    print(f"Number of email addresses found: {len(info_list)}")
    print(f"Were all email addresses scraped unique? {all_unique(info_list)}")