from web_scraper import scrape_emails_from_website

def test_scraper_on_n_links(base_url, max_links):
    print(f"Testing scraper on the first {max_links} links of {base_url}")
    scraped_emails = scrape_emails_from_website(base_url, max_links)
    print(f"Found {len(scraped_emails)} emails:")
    for email in scraped_emails:
        print(email)

if __name__ == "__main__":
    base_url = "https://www.dlsu.edu.ph"  # Change this to your target website
    max_links = 1000  # Change this to the desired number of links to scrape
    test_scraper_on_n_links(base_url, max_links)
