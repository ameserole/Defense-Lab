import importlib
import json
import time
import structlog
import pika
from multiprocessing import Process
from threading import Thread
from ServiceManager import ServiceInfo, cleanupService

logger = structlog.get_logger()

def cleanupCallback(ch, method, properties, body):
    logger.info("cleanupCallback", msg="Recieved Message", body=body)
    body = json.loads(body)
    service = ServiceInfo(body)
    log = logger.bind(service=service.__dict__)
    log.info("cleanupCallback", msg="Cleaning Up Service") 
    cleanupService(service)
    ch.basic_ack(delivery_tag = method.delivery_tag)
    log.info("cleanupCallback", msg="Service Cleanup Done")
    

def cleanupWorker():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='cleanupQueue', durable=True)
    logger.info("cleanupWorker", msg="Starting Cleanup Worker", queue="cleanupQueue")
    channel.basic_consume(cleanupCallback,queue='cleanupQueue')
    channel.start_consuming()

def startCleanupWorkers(numThreads):
    for i in range(numThreads):
        t = Process(target=cleanupWorker)
        t.daemon = True
        t.start()
