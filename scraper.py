import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

def extract_emails_from_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # Find all text that matches the email pattern
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', soup.get_text())

    print("In: " + url)
    return emails

def get_internal_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    internal_links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.startswith('/') or url in href:
            internal_links.append(href)
    return internal_links

def scrape_emails_from_website(base_url):
    all_emails = set()
    visited_urls = set()
    urls_to_visit = [base_url]

    while urls_to_visit:
        current_url = urls_to_visit.pop(0)
        if current_url in visited_urls:
            continue

        visited_urls.add(current_url)

        internal_links = get_internal_links(current_url)
        for link in internal_links:
            absolute_url = urljoin(base_url, link)
            if absolute_url not in visited_urls and absolute_url not in urls_to_visit:
                urls_to_visit.append(absolute_url)

        emails_on_page = extract_emails_from_page(current_url)
        all_emails.update(emails_on_page)

    return all_emails

if __name__ == "__main__":
    # URL to scrape
    # url = 'https://www.dlsu.edu.ph'
    # url = 'https://www.imf.org/external/np/exr/contacts/contacts.aspx'
    # url = 'books.toscrape.com'
    website_url = "https://www.dlsu.edu.ph"
    scraped_emails = scrape_emails_from_website(website_url)

    print("Scraped emails:")
    for email in scraped_emails:
        print(email)
