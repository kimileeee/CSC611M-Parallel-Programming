import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import os
import csv
from datetime import datetime

def cfDecodeEmail(encodedString):
    """
    Decodes a protected email address
    """
    r = int(encodedString[:2],16)
    email = ''.join([chr(int(encodedString[i:i+2], 16) ^ r) for i in range(2, len(encodedString), 2)])
    return email

def allUnique(lis):
    """
    Checks if all elements in a list are unique
    """
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
    """
    Gets all the links from a page
    """
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
    """
    Extracts email addresses from a page
    """
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
    """
    Extracts email addresses from links within a page
    """
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
    """
    Writes the web scraping statistics to a TXT file
    """
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