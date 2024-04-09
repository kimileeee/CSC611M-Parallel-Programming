import pika
import json
from scraping_modules import extractEmailsFromLinks, extractEmailsFromPage

credentials = pika.PlainCredentials('rabbituser','rabbit1234')
parameters = pika.ConnectionParameters('<ip address>', 5672, '/', credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channel.queue_declare(queue='url_queue')

info_list = []

def callback(ch, method, properties, body):
    body = json.loads(body)
    try:
        curr_link = body.pop(0)
    except IndexError:
        print(f"URL list is empty, info scraping will be interrupted")
    except:
        print(f"Error encountered, info scraping will be interrupted")
    
    try:
        scraped_emails = extractEmailsFromPage(curr_link)
        scraped_emails.extend(extractEmailsFromLinks(curr_link))

        for email in scraped_emails:
            if email not in info_list:
                info_list.append(email)           
    except:
        print("Error encountered, info scraping skipped")

channel.basic_consume(queue='url_queue', on_message_callback=callback)
print('Starting Info Scraping, press CTRL+C to exit')

try:
    channel.start_consuming()
except KeyboardInterrupt:
        print('Exiting Info Scraping')