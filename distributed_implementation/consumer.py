import pika
import json
import time
import random
from scraping_modules import extractEmailsFromLinks, extractEmailsFromPage, writeEmailsToCSV, writeStatisticsToTXT

start_time = None
duration = None
info_list = []
scraped_urls = []

def paramsCallback(ch, method, properties, body):
    body = json.loads(body)

    global start_time, duration
    start_time = body[0]
    duration = body[1]

    print(f"Starting time: {start_time}")
    print(f"Duration: {duration / 60} minute/s")

    ch.stop_consuming()
    ch.close

def infoScraperCallback(ch, method, properties, body):
    global start_time, duration, info_list, scraped_urls
    
    if duration - 2 <= time.time() - start_time:
        print("Set duration reached, writing to output files and exiting")
        writeEmailsToCSV(info_list)
        writeStatisticsToTXT(scraped_urls, info_list)
        ch.stop_consuming()
        ch.close()
        return
        
    body = json.loads(body)

    try:
        curr_link = body.pop(0)
    except IndexError:
        print(f"URL list is empty, info scraping will be interrupted")
        return
    except:
        print(f"Error encountered, info scraping will be interrupted")
        return

    try:
        scraped_emails = extractEmailsFromPage(curr_link)
        scraped_emails.extend(extractEmailsFromLinks(curr_link))

        print(f"From URL {curr_link}")
        scraped_urls.append(curr_link)

        for email in scraped_emails:
            if email not in info_list:
                print(f"Found unique email {email[1]} with the name {email[0]}")
                info_list.append(email)           
    except:
        print("Error encountered, info scraping skipped")
        return

def setupConsumer(queue_name, callback):
    credentials = pika.PlainCredentials('rabbituser','rabbit1234')
    parameters = pika.ConnectionParameters('10.0.2.15', 5672, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.basic_qos(prefetch_count=2)

    if queue_name == "":
        channel.exchange_declare(exchange='logs', exchange_type='fanout')
        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        channel.queue_bind(exchange='logs', queue=queue_name)
    else:
        channel.queue_declare(queue=queue_name)
        channel.queue_purge(queue=queue_name)

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    if queue_name != "url_queue":
        print("Waiting for parameters")
    else:
        print("Parameters set, starting Info Scraper")

    channel.start_consuming()

if __name__ == "__main__":
    setupConsumer("", paramsCallback)
    setupConsumer("url_queue", infoScraperCallback)
