import json
import pika

from ServiceManager import buildImage

imageName = "sampleservice"
info = {
    'serviceName': 'over_write_1',
    'imageName': imageName,
    'exploitModule': 'overwriteLocalVar',
    'servicePort': 4322,
    'serviceHost': '',
    'serviceCheckName': 'SampleService'
}

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='serviceQueue', durable=True)
channel.basic_publish(exchange='',
                      routing_key='serviceQueue',
                      body=json.dumps(info))

info = {
    'serviceName': 'over_write_2',
    'imageName': imageName,
    'exploitModule': 'overwriteLocalVar',
    'servicePort': 4322,
    'serviceHost': '',
    'serviceCheckName': 'SampleService'
}
channel.basic_publish(exchange='',
                      routing_key='serviceQueue',
                      body=json.dumps(info))
connection.close()
