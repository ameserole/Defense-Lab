import argparse
import pika
import os
import sys
import binascii
import json
from DefenseLab import config


def callback(ch, method, properties, body):
    print body
    ch.basic_ack(delivery_tag=method.delivery_tag)
    sys.exit()
    return


def serviceStart(args):
    connection = pika.BlockingConnection(pika.ConnectionParameters(config.RABBITMQ_SERVER))
    channel = connection.channel()
    channel.queue_declare(queue='serviceQueue', durable=True)

    userInfo = binascii.hexlify(os.urandom(32)).decode('ascii')

    service = {
        'serviceName': args.service_name,
        'imageName': args.image_name,
        'volumeLocation': args.volume,
        'exploitModule': args.exploit,
        'serviceCheckName': args.service_check,
        'serviceHost': None,
        'servicePort': args.port,
        'userInfo': userInfo
    }

    print "Pushing: {}".format(service)
    channel.basic_publish(exchange='',
                          routing_key='serviceQueue',
                          body=json.dumps(service))

    connection = pika.BlockingConnection(pika.ConnectionParameters(config.RABBITMQ_SERVER))
    userChannel = connection.channel()
    userChannel.exchange_declare(exchange='resultX', exchange_type='direct')
    userChannel.queue_declare(queue='resultQueue', durable=True)

    userChannel.queue_bind(exchange='resultX',
                           queue='resultQueue',
                           routing_key=userInfo)

    print "Waiting for result"

    userChannel.basic_consume(callback, queue='resultQueue')
    userChannel.start_consuming()

    userChannel.close()


def labStart(args):
    if args.attack_workers is not None:
        config.NUM_ATTACK_WORKERS = args.attack_workers
    if args.service_workers is not None:
        config.NUM_SERVICE_WORKERS = args.service_workers
    if args.cleanup_workers is not None:
        config.NUM_CLEANUP_WORKERS = args.cleanup_workers
    from DefenseLab import DefenseLab # NOQA


def main():
    parser = argparse.ArgumentParser(description="Command Line Interface for Defense Lab")

    subparsers = parser.add_subparsers(title="Lab Commands", help="Commands to start and interact with Defense Lab", description="Commands to start and interact with Defense Lab")

    startArgs = subparsers.add_parser("start", help="Start up the defense lab", description="Start up the defense lab")
    startArgs.add_argument("-wa", "--attack-workers", type=int, help="Number of attack workers to start with. Default is two.")
    startArgs.add_argument("-ws", "--service-workers", type=int, help="Number of service workers to start with. Default is two.")
    startArgs.add_argument("-wc", "--cleanup-workers", type=int, help="Number of cleanup workers to start with. Default is two.")

    serviceArgs = subparsers.add_parser("send", description="Info to push onto the service queue")
    serviceArgs.add_argument("-s", "--service-name", required=True, help="Name of docker container to create")
    serviceArgs.add_argument("-i", "--image-name", required=True, help="Name of docker image to use")
    serviceArgs.add_argument("-v", "--volume", required=True, help="Location of files to test")
    serviceArgs.add_argument("-e", "--exploit", required=True, help="Name of exploit module to use")
    serviceArgs.add_argument("-c", "--service-check", required=True, help="Name of service check module to use")
    serviceArgs.add_argument("-p", "--port", required=True, type=int, help="Port number of service")

    args = parser.parse_args()

    try:
        args.attack_workers
        labStart(args)
    except AttributeError:
        serviceStart(args)


if __name__ == '__main__':
    main()
