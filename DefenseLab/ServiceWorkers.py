import json
import time
import structlog
import pika
from multiprocessing import Process
from threading import Thread
from ServiceManager import ServiceInfo, startService, cleanupService

logger = structlog.get_logger()

def serviceCallback(ch, method, properties, body):
    logger.info("serviceCallback", msg="Recieved Message", body=body)
    body = json.loads(body)
    service = ServiceInfo(body)
    log = logger.bind(serviceInfo=service.__dict__)
    log.info("serviceCallback", msg="Starting Service")
    service = startService(service)
    log.info("serviceCallback", msg="Placing Service on Attack Queue")
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='attackQueue', durable=True)
    channel.basic_publish(exchange='',
                          routing_key='attackQueue',
                          body=json.dumps(service.__dict__))

    ch.basic_ack(delivery_tag = method.delivery_tag)
    log.info("serviceCallback", msg="serviceCallback Done")
    

def serviceWorker():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='serviceQueue', durable=True)
    logger.info("serviceWorker", msg="Starting Service Worker", queue="serviceQueue")
    channel.basic_consume(serviceCallback,queue='serviceQueue')
    channel.start_consuming()

def startServiceWorkers(numThreads):
    for i in range(numThreads):
        t = Process(target=serviceWorker)
        t.daemon = True
        t.start()

