# from web_scraper import scrape, write_to_csv
# from web_scraper_parallel import scrape, write_to_csv
import web_scraper
import web_scraper_parallel
import web_scraper_producer_consumer

def test01(base_url):
    print(f"Testing scraper for 1 minute without parallelization")
    scraped_data = web_scraper.scrape(base_url, 60, 8)      # url, scraping_time, num_processes
    web_scraper.write_to_csv(scraped_data)

def test02(base_url):
    print(f"Testing scraper for 1 minute with parallelization")
    scraped_data = web_scraper_parallel.scrape(base_url, 60, 8)      # url, scraping_time, num_processes
    web_scraper_parallel.write_to_csv(scraped_data)

def test03(base_url):
    print(f"Testing scraper for 1 minute with producer-consumer model")
    scraped_data = web_scraper_producer_consumer.scrape(base_url, 60, 8)      # url, scraping_time, num_processes
    web_scraper_producer_consumer.write_to_csv(scraped_data)

if __name__ == "__main__":
    # base_url = "https://www.dlsu.edu.ph"  # Change this to your target website
    base_url = "https://www.dlsu.edu.ph/colleges/ccs/office-of-the-dean/"
    # base_url = "https://www.dlsu.edu.ph/colleges/ccs/faculty-profile/"
    # base_url = "https://www.dlsu.edu.ph/colleges/cla/office-of-the-dean/"

    # test01(base_url)      # web_scraper.py
    # test02(base_url)        # web_scraper_parallel.py
    test03(base_url)        # web_scraper_producer_consumer.py
