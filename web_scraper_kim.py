import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import re
import csv
from datetime import datetime
import time
import os
from utils import decode_email, write_to_csv, get_input, find_preceding_label, is_valid_domain, is_content_link

def get_soup(url):
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


def get_all_links(soup, base_url="https://www.dlsu.edu.ph"):
    if soup is None:
        return set()
    links = set()
    for link in soup.find_all('a', href=True):
        href = link['href']
        if not href.startswith('http'):
            href = urljoin(base_url, href)
        if is_valid_domain(href) and is_content_link(href):
            links.add(href)
    return links

def fetch_emails_and_names(soup, existing_emails):
    """
    Fetches emails and their corresponding texts/names
    """
    if soup is None:
        return []
    
    scraped_data = []

    # Find and decode protected email addresses and their texts
    emails = soup.select('a[href^="/cdn-cgi/l/email-protection"]')
    
    for e in emails:
        name = None
        text = e.get_text(strip=True)

        if text and text != "[email protected]":
            name = text
        # else: find way to get name

        decoded_email = None
        if 'data-cfemail' in e.attrs:
            name = find_preceding_label(e) if not name else name
            encoded_email = e['data-cfemail']
            decoded_email = decode_email(encoded_email)
        else:
            split_email = e['href'].split('#')
            if len(split_email) == 2:
                encoded_email = split_email[1]
                decoded_email = decode_email(encoded_email)

        # Only add data if email is not already in the list
        if decoded_email and decoded_email not in existing_emails:
            if not name:
                name = "No name found"
            scraped_data.append([name, decoded_email])

    return scraped_data


def scrape(base_url="https://dlsu.edu.ph", scraping_time=60, num_processes=4):
    """
    Data being accessed and modified:
        urls_to_visit, visited_urls, emails_data

    For statistics:
        url = base_url
        number of pages scraped = len(visited_urls)
        number of email addresses found = len(emails_data)   *Note: make sure emails are unique
    """
    start_time = time.time()  # Record the start time

    urls_to_visit = {base_url}
    visited_urls = set()
    emails_data = {}

    while urls_to_visit and (time.time() < start_time + scraping_time):
        current_url = urls_to_visit.pop()                                   # Getting the last URL from the urls_to_visit set
       
        print(f"Visiting: {current_url}")
        visited_urls.add(current_url)                                       # Writing to the visited_urls set

        soup = get_soup(current_url)
        if soup:
            emails_and_texts = fetch_emails_and_names(soup, emails_data.keys())                 # Fetches emails and their corresponding texts/names
            for name, email in emails_and_texts:
                emails_data[email] = (name, current_url)                                   # Writing to emails_data list

        for link in get_all_links(get_soup(current_url), base_url):
            if link not in visited_urls:                                    # Accessing visited_urls set
                urls_to_visit.add(link)                                     # Writing to the urls_to_visit set

    print("-----------------------------------")
    print(f"Started scraping at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")
    print(f"Finished scraping at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}")
    print(f"URL: {base_url}")
    print(f"Scraped {len(visited_urls)} pages and found {len(emails_data)} emails.\n")
    
    return emails_data

if __name__ == "__main__":
    # INPUT
    base_url, scraping_time, num_processes = get_input()

    # SCRAPING
    scraped_data = scrape(base_url, scraping_time, num_processes)

    # OUTPUT
    write_to_csv(scraped_data)
