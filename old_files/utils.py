import csv
from datetime import datetime
import os
from urllib.parse import urlparse

DEFAULT_BASE_URL = "https://www.dlsu.edu.ph"
MAX_PAGES = 250

def is_content_link(url):
    """
    Checks if the URL is not a content link
    """
    content_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.zip', '.rar', '.exe', '.dmg', '.csv', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.mpg', '.mpeg']
    return not any(url.lower().endswith(ext) for ext in content_extensions)

def is_valid_domain(url, base_domain='dlsu.edu.ph'):
    """
    Checks if the URL is within the base domain
    """
    parsed_url = urlparse(url)
    return base_domain in parsed_url.netloc

# def find_emails(soup):
#     if soup is None:
#         return []
#     return re.findall(r'\b[A-Za-z0-9._%+-]+@dlsu\.edu\.ph\b', soup.get_text(), re.I)

def decode_email(encoded_email):
    """
    Decodes a protected email address
    """
    r = int(encoded_email[:2],16)
    email = ''.join([chr(int(encoded_email[i:i+2], 16) ^ r) for i in range(2, len(encoded_email), 2)])
    return email

def find_preceding_label(element):
    """
    Attempts to find a descriptive label for an element
    """
    # Attempt to find a preceding sibling or parent with text
    for sibling in element.previous_siblings:
        if sibling.string and sibling.string.strip():
            return sibling.string.strip()
    parent = element.find_parent()
    if parent and parent.string and parent.string.strip():
        return parent.string.strip()
    # Fallback in case no descriptive label is found
    return "No label found"

def get_input():
    """
    Gets the input from the user
    """
    base_url = input("Enter base URL: ")
    scraping_time = int(input("Enter scraping time (minutes): "))
    num_processes = int(input("Enter number of processes: "))
    return base_url, scraping_time, num_processes

def write_to_csv(emails_data):
    """
    Writes the scraped data to a CSV file
    """
    os.makedirs("output", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"Output_{timestamp}.csv"
    filepath = os.path.join("output", filename)
    with open(filepath, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'Email', 'URL'])
        for email, (name, url) in emails_data.items():
            writer.writerow([name, email, url])

    print(f"Data written to {filepath}\n")