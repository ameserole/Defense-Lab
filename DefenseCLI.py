#from DefenseLab import DefenseLab
import argparse
import pika
import os
import sys
import binascii
import json

def callback(ch, method, properties, body):
    print body
    ch.basic_ack(delivery_tag = method.delivery_tag)
    sys.exit()
    return

def main():
    parser = argparse.ArgumentParser(description="Command Line Interface for Defense Lab")

    parser.add_argument("-s", "--service-name", required=True, help="Name of docker container to create")
    parser.add_argument("-i", "--image-name", required=True, help="Name of docker image to use")
    parser.add_argument("-v", "--volume", required=True, help="Location of files to test")
    parser.add_argument("-e", "--exploit", required=True, help="Name of exploit module to use")
    parser.add_argument("-c", "--service-check", required=True, help="Name of service check module to use")
    parser.add_argument("-p", "--port", required=True, type=int, help="Port number of service")

    args = parser.parse_args()


    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
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


    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    userChannel = connection.channel()
    userChannel.exchange_declare(exchange='resultX')
    userChannel.queue_declare(queue='resultQueue', durable=True)


    userChannel.queue_bind(exchange='resultX',
                           queue='resultQueue',
                           routing_key=userInfo)

    print "Waiting for result"

    userChannel.basic_consume(callback, queue='resultQueue')
    userChannel.start_consuming()

    userChannel.close()

if __name__ == '__main__':
    main()
