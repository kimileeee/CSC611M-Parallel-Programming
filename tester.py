from web_scraper import scrape, write_to_csv
import time

def test01(base_url):
    print(f"Testing scraper for 1 minute without parallelization")
    scraped_data = scrape(base_url, 60, 4)      # url, scraping_time, num_processes
    write_to_csv(scraped_data)

def test02(base_url, max_links):
    pass


if __name__ == "__main__":
    # base_url = "https://www.dlsu.edu.ph"  # Change this to your target website
    base_url = "https://www.dlsu.edu.ph/colleges/ccs/office-of-the-dean/"
    # base_url = "https://www.dlsu.edu.ph/colleges/ccs/faculty-profile/"
    # base_url = "https://www.dlsu.edu.ph/colleges/cla/office-of-the-dean/"

    test01(base_url) # web_scraper.py
    # test02(base_url, max_links) # web_scraper_parallel.py
