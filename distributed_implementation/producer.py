import pika
import json
import time
import random
from scraping_modules import getLinks

start_time = None
duration = None
starting_url = None

def sendParams():
    global start_time, duration, starting_url
    credentials = pika.PlainCredentials('rabbituser','rabbit1234')
    parameters = pika.ConnectionParameters('10.0.2.15', 5672, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.exchange_declare(exchange='logs', exchange_type='fanout')

    start_time = time.time()
    duration = input("Enter the duration for link scraping (in minutes): ")
    duration = int(duration) * 60
    # starting_url = "https://www.dlsu.edu.ph"
    starting_url = input("Enter web scraping starting point: ")
    params_message = [start_time, duration, starting_url]

    channel.basic_publish(exchange='logs', routing_key='', body=json.dumps(params_message))
    connection.close()

def sendLinks():
    global start_time, duration, starting_url
    credentials = pika.PlainCredentials('rabbituser','rabbit1234')
    parameters = pika.ConnectionParameters('10.0.2.15', 5672, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue='url_queue')

    url_list = []
    visited_list = []
    to_scrape = []

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

        if curr_url in visited_list and curr_url in url_list:
            continue

        visited_list.append(curr_url)

        try:
            found_links = getLinks(curr_url)

            for link in found_links:
                if link not in visited_list and link not in url_list and "https://www.dlsu.edu.ph/" in link:
                    print(f"Added URL to list: {link}")
                    url_list.append(link)
                    to_scrape.append(link)
        except:
            print("Error encountered, link scraping skipped")
            continue

        channel.basic_publish(exchange='', routing_key='url_queue', body=json.dumps(to_scrape))
        to_scrape = []

    connection.close()

if __name__ == "__main__":   
    sendParams()
    sendLinks()
