import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from multiprocessing import Process, Manager
import time
import re
import os
import csv
from datetime import datetime
import random

def cfDecodeEmail(encodedString):
    r = int(encodedString[:2],16)
    email = ''.join([chr(int(encodedString[i:i+2], 16) ^ r) for i in range(2, len(encodedString), 2)])
    return email

def all_unique(lis):
    return len(set(lis)) == len(lis)

def getSoup(url):
    """
    Accesses and returns the BeautifulSoup object of the URL. Gets HTML content.
    """
    try:
        response = requests.get(url, timeout=10)
        # Skip non-HTML content based on Content-Type header
        if 'text/html' not in response.headers.get('Content-Type', ''):
            return None
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup
    except requests.exceptions.TooManyRedirects:        # Redirect loop or a problematic URL
        print(f"Too many redirects: {url}")
    except Exception as e:                              # Other exceptions
        print(f"Failed to access {url}: {e}")
    return None

def getLinks(url):
    # response = requests.get(url=url)
    # soup = BeautifulSoup(response.content, 'html.parser')
    soup = getSoup(url)
    if soup is None:
        return []
    
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
    # response = requests.get(url)
    # soup = BeautifulSoup(response.content, 'html.parser')
    soup = getSoup(url)
    if soup is None:
        return []
    
    encoded_emails = soup.find_all('a', {"class": "__cf_email__"})
    unprotected_emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', soup.get_text())
    collected_emails = []
    
    for i in range(len(encoded_emails)):
        name = None
        text = encoded_emails[i].get_text(strip=True)

        if text and text != "[email protected]":
            name = text

        encoded = encoded_emails[i]['data-cfemail']
        decoded = cfDecodeEmail(encoded)
        if not name:
            email_name = decoded.split('@')[0]
            if "." in email_name:
                first_name = email_name.split('.')[0].capitalize()
                last_name = email_name.split('.')[-1].capitalize()
                name = f"{first_name} {last_name}"
            else:
                name = "No name found"
        
        collected_emails.append([name, decoded])

    for email in unprotected_emails:
        collected_emails.append(["No name found", email])

    if len(collected_emails) != 0:
        print(f"Email addresses collected from {url}: {collected_emails}")

    return collected_emails

def extractEmailsFromLinks(url):
    # response = requests.get(url)
    # soup = BeautifulSoup(response.content, 'html.parser')
    soup = getSoup(url)
    if soup is None:
        return []
    
    links = soup.find_all('a')
    collected_emails = []

    for link in links:
        if 'href' in link.attrs:
            if link['href'].find("/cdn-cgi/l/email-protection#") == -1:
                continue
            else:
                encoded = link['href'].removeprefix("https://www.dlsu.edu.ph/cdn-cgi/l/email-protection#")
                decoded = cfDecodeEmail(encoded)
                name = "No name found"
                text = link.get_text(strip=True)
                if text and text != "[email protected]":
                    name = text

                collected_emails.append([name, decoded])
        else:
            continue

    if len(collected_emails) != 0:
        print(f"Email address collected from links within {url}: {collected_emails}")
        
    return collected_emails

def writeEmailsToCSV(info_list):
    """
    Writes the scraped data to a CSV file
    """
    os.makedirs("output", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"EmailData_{timestamp}.csv"
    filepath = os.path.join("output", filename)
    with open(filepath, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'Email'])
        for email, name in info_list.items():
            writer.writerow([name, email])

    print(f"Data written to {filepath}\n")

def writeStatisticsToTXT(completed_list, info_list, start_time, end_time, execution_time, starting_url, link_scraper_count, info_scraper_count):
    os.makedirs("output", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"ScrapingStats_{timestamp}.txt"
    filepath = os.path.join("output", filename)
    with open(filepath, 'w', newline='', encoding='utf-8') as file:
        file.write(f"Website scraped: {starting_url}\n")
        file.write(f"Number of pages scraped: {len(completed_list)}\n")
        file.write(f"Number of email addresses found: {len(info_list)}\n")
        file.write("\n")
        file.write(f"Start time: {datetime.fromtimestamp(start_time)}\n")
        file.write(f"End time: {datetime.fromtimestamp(end_time)}\n")
        file.write(f"Execution time: {datetime.fromtimestamp(execution_time).strftime('%M:%S')}\n")
        file.write(f"Number of processes allocated for link scraping: {link_scraper_count}\n")
        file.write(f"Number of processes allocated for info scraping: {info_scraper_count}\n")

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

        while time.time() - self.start_time <= self.duration * 60:
            print(f"LinkScraper {self.ID} running")

            try:
                curr_url = self.url_list.pop(0)
            except IndexError:
                time_delay = random.uniform(0.1, 0.5)
                print(f"URL list is empty, link scraping will be interrupted for {time_delay} seconds")
                time.sleep(time_delay)
                continue
            except:
                print(f"Error encountered, link scraping will be interrupted")
                continue

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
                print("Error encountered, link scraping skipped")
                continue

        print(f"LinkScraper {self.ID} has finished link scraping")

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

        while time.time() - self.start_time <= self.duration * 60:
            print(f"InfoScraper {self.ID} running")

            try:
                curr_link = self.visited_list.pop(0)
            except IndexError:
                time_delay = random.uniform(0.5, 1)
                print(f"Visited list is empty, info scraping will be interrupted for {time_delay} seconds")
                time.sleep(time_delay)
                continue
            except:
                print(f"Error encountered, info scraping will be interrupted")
                continue

            if curr_link in self.visited_list or curr_link in self.completed_list:
                continue

            self.completed_list.append(curr_link)

            try:
                scraped_emails = extractEmailsFromPage(curr_link)
                scraped_emails.extend(extractEmailsFromLinks(curr_link))

                for name, email in scraped_emails:
                    if email not in self.info_list.keys():
                        # self.info_list.append(email)
                        self.info_list[email] = name
                        print(f"InfoScraper {self.ID} found something - current email list: {self.info_list}")
                    
            except:
                print("Error encountered, info scraping skipped")
                continue
        
        print(f"InfoScraper {self.ID} has finished info scraping")

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
    info_list = manager.dict()
    processes = []
    
    start_time = time.time()

    for i in range(link_scraper_count):
        link_scraper = LinkScraper(i, starting_url, url_list, visited_list, completed_list, start_time, duration)
        link_scraper.start()
        processes.append(link_scraper)

    print("Sleeping for 1 second to give link scrapers some time to generate initial links")
    time.sleep(1)

    for i in range(info_scraper_count):
        info_scraper = InfoScraper(i, visited_list, completed_list, info_list, start_time, duration)
        info_scraper.start()
        processes.append(info_scraper)

    for p in processes:
        p.join()

    end_time = time.time()
    execution_time = end_time - start_time

    writeEmailsToCSV(info_list)
    writeStatisticsToTXT(completed_list, info_list, start_time, end_time, execution_time, starting_url, link_scraper_count, info_scraper_count)

    print(f"Execution time: {execution_time:2.2f}")

    print(f"Number of pages scraped: {len(completed_list)}")
    print(f"Were all pages scraped unique? {all_unique(completed_list)}")
    print(f"Number of email addresses found: {len(info_list)}")
    print(f"Were all email addresses scraped unique? {all_unique(info_list)}")