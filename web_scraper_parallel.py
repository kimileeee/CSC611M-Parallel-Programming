import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import time
from utils import decode_email, write_to_csv, get_input, find_preceding_label, is_valid_domain, is_content_link
from multiprocessing import Process, Manager, Queue


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

def worker_process(url_queue, visited_urls, emails_data, base_url, start_time, scraping_time):
    while not url_queue.empty() and (time.time() < start_time + scraping_time):
        current_url = url_queue.get()  # Get URL from the queue
        if current_url not in visited_urls:
            print(f"Visiting: {current_url}")
            visited_urls.append(current_url)
            soup = get_soup(current_url)
            if soup:
                emails_and_texts = fetch_emails_and_names(soup, emails_data.keys())
                for name, email in emails_and_texts:
                    emails_data[email] = (name, current_url)    # Add email, name, and url to the dictionary
                for link in get_all_links(soup, base_url):
                    if link not in visited_urls:
                        url_queue.put(link)  # Add new URL to the queue


def scrape(base_url="https://dlsu.edu.ph", scraping_time=60, num_processes=4):
    start_time = time.time()
    manager = Manager()

    # Shared data structures
    urls_to_visit = manager.Queue()
    urls_to_visit.put(base_url)  # Start with the base URL
    visited_urls = manager.list()
    emails_data = manager.dict()

    # Create worker processes and start them
    processes = []
    for _ in range(num_processes):
        p = Process(target=worker_process, args=(urls_to_visit, visited_urls, emails_data, base_url, start_time, scraping_time))
        processes.append(p)
        p.start()

    # Join processes
    for p in processes:
        p.join()

    print("-----------------------------------")
    print(f"Started scraping at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")
    print(f"Finished scraping at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}")
    print(f"URL: {base_url}")
    print(f"Scraped {len(visited_urls)} pages and found {len(emails_data)} emails.\n")
    
    return dict(emails_data)  # Convert Manager dict back to regular dict for further use

if __name__ == "__main__":
    # INPUT
    base_url, scraping_time, num_processes = get_input()

    # SCRAPING
    scraped_data = scrape(base_url, scraping_time, num_processes)

    # OUTPUT
    write_to_csv(scraped_data)
