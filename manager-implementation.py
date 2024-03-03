import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from multiprocessing import Process, Manager
import time
import re
import random

def cfDecodeEmail(encodedString):
    r = int(encodedString[:2],16)
    email = ''.join([chr(int(encodedString[i:i+2], 16) ^ r) for i in range(2, len(encodedString), 2)])
    return email

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

    return emails

class LinkScraper(Process):
    def __init__(self, ID, starting_point, url_list, visited_list):
        Process.__init__(self)
        self.ID = ID
        self.starting_point = starting_point
        self.url_list = url_list
        self.visited_list = visited_list
    def run(self):
        self.url_list.append(self.starting_point)

        while self.url_list:
            print("LinkScraper running")
            curr_url = self.url_list.pop(0)

            if curr_url in self.visited_list or curr_url in self.url_list:
                continue

            self.visited_list.append(curr_url)

            try:
                found_links = getLinks(curr_url)

                for link in found_links:
                    if link not in self.visited_list and link not in self.url_list and "https://www.dlsu.edu.ph/" in link:
                        self.url_list.append(link)
                        print(f"LinkScraper {self.ID} added {link}")
                
                random.shuffle(self.url_list)

            except:
                print("Error encountered, info scraping skipped")
                continue

class InfoScraper(Process):
    def __init__(self, ID, url_list, info_list):
        Process.__init__(self)
        self.ID = ID
        self.url_list = url_list
        self.info_list = info_list
    def run(self):

        while self.url_list:
            print(f"InfoScraper {self.ID} running")
            curr_link = self.url_list.pop(0)

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
    start_time = time.time()

    starting_url = "https://www.dlsu.edu.ph"
    manager = Manager()
    url_list = manager.list()
    visited_list = manager.list()
    info_list = manager.list()
    processes = []

    link_scraper = LinkScraper(0, starting_url, url_list, visited_list)
    link_scraper.start()
    processes.append(link_scraper)
    
    print("Sleeping for 5 seconds to initiate link scraper")
    time.sleep(5)

    for i in range(3):
        info_scraper = InfoScraper(i, url_list, info_list)
        info_scraper.start()
        processes.append(info_scraper)

    for p in processes:
        p.join()


    print(f"Number of pages scraped: {len(visited_list)}")
    print(f"Number of email addresses found: {len(info_list)}")

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time:.2f} seconds")