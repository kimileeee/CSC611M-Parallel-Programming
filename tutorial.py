from bs4 import BeautifulSoup
import requests, re
import csv

# URL to scrape
# url = 'https://www.dlsu.edu.ph'
# url = 'https://www.imf.org/external/np/exr/contacts/contacts.aspx'
url = 'books.toscrape.com'


# Email regex
# email_regex = '([a-zA-Z0-9+._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)'
email_regex = '\w+@\w+\.\w+'
email_id = re.compile(email_regex)

req = requests.get(url)
soup = BeautifulSoup(req.content, "html.parser")

res = soup.title
emails = soup.find_all()
# emails = soup.find_all(string=email_id)

# print(soup.get_text())
print(res.get_text())
for e in emails:
    print(e)



### MP SPECIFICATIONS
## INPUT:
# URL of the website to be scraped
# Scraping time in minutes
# Optional: Number of threads / process to use

## OUTPUT:
# Text file that contains email and its associated name, office, department or unit 
#     in CSV format
# Text file that contains statistics of the website: URL, number of pages scraped and
#     number of email addresses found