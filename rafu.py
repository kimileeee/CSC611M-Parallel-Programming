import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from multiprocessing import Process, Manager
import time
import random
import re

def cfDecodeEmail(encodedString):
    r = int(encodedString[:2],16)
    email = ''.join([chr(int(encodedString[i:i+2], 16) ^ r) for i in range(2, len(encodedString), 2)])
    return email

def extractEmailsFromPage(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    encoded_emails = soup.find_all('a', {"class": "__cf_email__"})
    scraped_emails = []
    
    for i in range(len(encoded_emails)):
        encoded = encoded_emails[i]['data-cfemail']
        decoded = cfDecodeEmail(encoded)
        scraped_emails.append(decoded)

    unprotected_emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', soup.get_text())
    scraped_emails.extend(unprotected_emails)

    if len(scraped_emails) != 0:
        print(f"Emails found in url: {url}")

    return scraped_emails

def getLinks(base_url):
    response = requests.get(url=base_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find_all('a')

    found_links = []

    for link in links:
        if 'href' in link.attrs:
                if link['href'].find(".pdf") != -1:
                    continue
                else:
                    found_links.append(urljoin(base_url, link['href']))
        else:
            continue

    return found_links

def scraper(base_url, limit, email_list, visited_list, url_list):

    url_list.append(base_url)

    while url_list and len(email_list) < limit:
        curr_url = url_list.pop(0)
        if curr_url in visited_list:
            continue

        visited_list.append(curr_url)

        try:
            linksToScrape = getLinks(curr_url)
            random.shuffle(linksToScrape)
        except:
            continue

        for link in linksToScrape:
            if link not in visited_list and link not in url_list:
                url_list.append(link)

        print(f"Current url: {curr_url}")
        email_list.extend(extractEmailsFromPage(curr_url))

if __name__ == "__main__":

    start_time = time.time()

    base_url = "https://www.dlsu.edu.ph/"
    limit = 10

    manager = Manager()
    email_list = manager.list()
    visited_list = manager.list()
    url_list = []

    processes = []

    for i in range(8):
        process = Process(target=scraper, args=(base_url, limit, email_list, visited_list, url_list))
        process.start()
        processes.append(process)
    
    for p in processes:
        p.join()

    end_time = time.time()
    execution_time = end_time - start_time

    print(f"Execution time: {execution_time:.2f} seconds")
    print(email_list)
