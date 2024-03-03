import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from multiprocessing import Process, Pipe
import time
import re

def cfDecodeEmail(encodedString):
    r = int(encodedString[:2],16)
    email = ''.join([chr(int(encodedString[i:i+2], 16) ^ r) for i in range(2, len(encodedString), 2)])
    return email

def getLinks(url):
    response = requests.get(url=url)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find_all('a')

    found_links = []

    for link in links:
        if 'href' in link.attrs:
            if link['href'].find(".pdf") != -1:
                continue
            else:
                linkToScrape = urljoin(url, link['href'])
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

class LinkScraper(Process):
    def __init__(self, ID, starting_point, producer_pipe):
        Process.__init__(self)
        self.ID = ID
        self.starting_point = starting_point
        self.producer_pipe = producer_pipe
        self.url_list = []
        self.visited_list = []
    def run(self):
        self.url_list.append(self.starting_point)

        while self.url_list:
            curr_url = self.url_list.pop(0)

            if curr_url in self.visited_list:
                continue

            self.visited_list.append(curr_url)
            found_links = getLinks(curr_url)

            for link in found_links:
                print(f"LinkScraper {self.ID} sent {link}")
                self.producer_pipe.send(link)

        self.producer_pipe.close()

class InfoScraper(Process):
    def __init__(self, ID, consumer_pipe):
        Process.__init__(self)
        self.ID = ID
        self.consumer_pipe = consumer_pipe
        self.info_list = []
    def run(self):
        eof = False

        while not (eof):
            try:
                link = self.consumer_pipe.recv()
                scraped_emails = extractEmailsFromPage(link)
                print(f"InfoScraper {self.ID} found something. Current email list: {self.info_list}")
                self.info_list.extend(scraped_emails)
            except EOFError:
                print('No more data to process. Exitiing')
                eof = True 
        
if __name__ == "__main__":

    start_time = time.time()

    link_scraper_1, info_scraper_1 = Pipe(True)
    link_scraper_2, info_scraper_2 = Pipe(True)
    link_scraper_3, info_scraper_3 = Pipe(True)
    link_scraper_4, info_scraper_4 = Pipe(True)

    starting_url_list = ["https://www.dlsu.edu.ph/campuses/manila", "https://www.dlsu.edu.ph/laguna-campus", "https://www.dlsu.edu.ph/campuses/makati", "https://www.dlsu.edu.ph/campuses/rufino"]
    link_scrapers = [link_scraper_1, link_scraper_2, link_scraper_3, link_scraper_4]
    info_scrapers = [info_scraper_1, info_scraper_2, info_scraper_3, info_scraper_4]
    processes = []

    for i in range(4):
        link_scraper = LinkScraper(i, starting_url_list[i], link_scrapers[i])
        info_scraper = InfoScraper(i, info_scrapers[i])
        link_scraper.start()
        info_scraper.start()
        processes.append(link_scraper)
        processes.append(info_scraper)

    for p in processes:
        p.join()

    end_time = time.time()
    execution_time = end_time - start_time

    print(f"Execution time: {execution_time:.2f} seconds")