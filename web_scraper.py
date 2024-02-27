import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import re

def get_soup(url):
    try:
        response = requests.get(url, timeout=10)
        # Skip non-HTML content based on Content-Type header
        if 'text/html' not in response.headers.get('Content-Type', ''):
            return None
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup
    except requests.exceptions.TooManyRedirects:
        print(f"Too many redirects: {url}")
    except Exception as e:
        print(f"Failed to access {url}: {e}")
    return None

def find_emails(soup):
    if soup is None:
        return []
    return re.findall(r'\b[A-Za-z0-9._%+-]+@dlsu\.edu\.ph\b', soup.get_text(), re.I)

def get_all_links(soup, base_url):
    links = set()
    for link in soup.find_all('a', href=True):
        href = link['href']
        if not href.startswith('http'):
            href = urljoin(base_url, href)
        if is_valid_domain(href) and is_content_link(href):
            links.add(href)
    return links

def is_content_link(url):
    content_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.zip', '.rar', '.exe', '.dmg', '.csv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.mpg', '.mpeg']
    return not any(url.lower().endswith(ext) for ext in content_extensions)

def is_valid_domain(url, base_domain='dlsu.edu.ph'):
    parsed_url = urlparse(url)
    return base_domain in parsed_url.netloc

def scrape_emails_from_website(base_url, max_links=None):
    visited_urls = set()
    emails = set()
    urls_to_visit = {base_url}

    while urls_to_visit and (max_links is None or len(visited_urls) < max_links):
        current_url = urls_to_visit.pop()
        print(f"Visiting: {current_url}")
        visited_urls.add(current_url)

        soup = get_soup(current_url)
        if soup:
            emails.update(find_emails(soup))
            for link in get_all_links(soup, base_url):
                if link not in visited_urls:
                    urls_to_visit.add(link)

    return emails

if __name__ == "__main__":
    # URL to scrape
    # url = 'https://www.dlsu.edu.ph'
    # url = 'https://www.imf.org/external/np/exr/contacts/contacts.aspx'
    # url = 'books.toscrape.com'
    base_url = "https://www.dlsu.edu.ph"
    scraped_emails = scrape_emails_from_website(base_url)
    print(f"Found {len(scraped_emails)} emails:")
    for email in scraped_emails:
        print(email)
