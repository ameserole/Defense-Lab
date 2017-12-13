import json
import structlog
import pika
import config
from multiprocessing import Process
from ServiceManager import ServiceInfo, startService

logger = structlog.get_logger()


def serviceCallback(ch, method, properties, body):
    """Take service off of the queue and start it up in a container"""

    logger.info("serviceCallback", msg="Recieved Message", body=body)
    body = json.loads(body)
    service = ServiceInfo(body)
    log = logger.bind(serviceInfo=service.__dict__)
    log.info("serviceCallback", msg="Starting Service")

    # Reassign service with new ip address
    service = startService(service)

    log.info("serviceCallback", msg="Placing Service on Attack Queue")
    connection = pika.BlockingConnection(pika.ConnectionParameters(config.RABBITMQ_SERVER))
    channel = connection.channel()
    channel.queue_declare(queue='attackQueue', durable=True)
    channel.basic_publish(exchange='',
                          routing_key='attackQueue',
                          body=json.dumps(service.__dict__))

    ch.basic_ack(delivery_tag=method.delivery_tag)
    log.info("serviceCallback", msg="serviceCallback Done")


def serviceWorker():
    """Declare service queue and callback"""
    connection = pika.BlockingConnection(pika.ConnectionParameters(config.RABBITMQ_SERVER))
    channel = connection.channel()
    channel.queue_declare(queue='serviceQueue', durable=True)
    logger.info("serviceWorker", msg="Starting Service Worker", queue="serviceQueue")
    channel.basic_consume(serviceCallback, queue='serviceQueue')
    channel.start_consuming()


def startServiceWorkers(numThreads):
    """Start numThreads service workers"""
    for i in range(numThreads):
        t = Process(target=serviceWorker)
        t.daemon = True
        t.start()
