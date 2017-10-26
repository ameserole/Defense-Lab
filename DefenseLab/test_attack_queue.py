import json
import pika

from ServiceManager import buildImage

imageName = "apache-test2"
info = {
    'name': 'MyApache',
    'imageName': imageName,
    'exploitModule': 'sampleExploit'}

dockerfile = "/home/messy/Documents/tamuctf-dev/Defense-Lab/DefenseLab"
buildImage(dockerfile, imageName)

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='attackQueue', durable=True)
channel.basic_publish(exchange='',
                      routing_key='attackQueue',
                      body=json.dumps(info))
