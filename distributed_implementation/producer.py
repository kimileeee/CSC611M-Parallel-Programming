import pika
import json
import time
import random
from scraping_modules import getLinks

credentials = pika.PlainCredentials('rabbituser','rabbit1234')
parameters = pika.ConnectionParameters('<ip address>', 5672, '/', credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channel.queue_declare(queue='url_queue')

if __name__ == "__main__":   
    duration = input("Enter the duration for link scraping (in minutes): ")
    duration = int(duration) * 60
    starting_url = "https://www.dlsu.edu.ph"

    url_list = []
    visited_list = []
    to_scrape = []
    
    start_time = time.time()
    print("Starting Link Scraping")
    url_list.append(starting_url)

    while time.time() - start_time < duration:

        try:
            curr_url = url_list.pop(0)
        except IndexError:
            time_delay = random.uniform(0.1, 0.5)
            print(f"URL list is empty, link scraping will be interrupted for {time_delay} seconds")
            time.sleep(time_delay)
            continue
        except:
            print(f"Error encountered, link scraping will be interrupted")
            continue

        if curr_url in visited_list:
            continue

        try:
            found_links = getLinks(curr_url)

            for link in found_links:
                if link not in visited_list and "https://www.dlsu.edu.ph/" in link:
                    url_list.append(link)
                    to_scrape.append(link)
        except:
            print("Error encountered, link scraping skipped")
            continue

        channel.basic_publish(exchange='', routing_key='url_queue', body=json.dumps(to_scrape))
        to_scrape = []

    connection.close()