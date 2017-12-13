import json
import structlog
import pika
from multiprocessing import Process
from ServiceManager import ServiceInfo, cleanupService

logger = structlog.get_logger()


def cleanupCallback(ch, method, properties, body):
    """Take service off of queue and delete its corresponding container"""

    logger.info("cleanupCallback", msg="Recieved Message", body=body)
    body = json.loads(body)
    service = ServiceInfo(body)
    log = logger.bind(service=service.__dict__)
    log.info("cleanupCallback", msg="Cleaning Up Service")
    cleanupService(service)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    log.info("cleanupCallback", msg="Service Cleanup Done")


def cleanupWorker():
    """Declare cleanup queue and callback"""

    connection = pika.BlockingConnection(pika.ConnectionParameters(config.RABBITMQ_SERVER))
    channel = connection.channel()
    channel.queue_declare(queue='cleanupQueue', durable=True)
    logger.info("cleanupWorker", msg="Starting Cleanup Worker", queue="cleanupQueue")
    channel.basic_consume(cleanupCallback, queue='cleanupQueue')
    channel.start_consuming()


def startCleanupWorkers(numThreads):
    """Start numThreads cleanup workers"""
    for i in range(numThreads):
        t = Process(target=cleanupWorker)
        t.daemon = True
        t.start()
