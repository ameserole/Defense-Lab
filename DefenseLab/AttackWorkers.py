import importlib
import json
import structlog
import time
import pika
from multiprocessing import Process
from threading import Thread
from ServiceManager import ServiceInfo, startService, cleanupService, getLogs

logger = structlog.get_logger()

def cleanup(service, log):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='cleanupQueue', durable=True)
    channel.basic_publish(exchange='',
                          routing_key='cleanupQueue',
                          body=json.dumps(service.__dict__))

    log.info("attackCallback", msg="Attack Done")
  


def attackCallback(ch, method, properties, body):
    connection2 = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    resultChannel = connection2.channel()
    resultChannel.exchange_declare(exchange='resultX')
    resultChannel.queue_declare(queue='resultQueue', durable=True)
    
    body = json.loads(body)
    logger.info("attackCallback", msg="Recieved Message", body=body)
    service = ServiceInfo(body)
    
    resultChannel.queue_bind(exchange='resultX', queue='resultQueue', routing_key=str(service.userInfo))

    log = logger.bind(service=service.__dict__)
    userMsg = "Starting Attack on {}\n".format(service.serviceName)
    
    serviceCheckModuleName = 'Services.' + service.serviceCheckName + '.' + service.serviceCheckName
    serviceModule = importlib.import_module(serviceCheckModuleName, package=None)
    serviceCheckObject = serviceModule.ServiceCheck(service)


    if serviceCheckObject.checkService():
        log.info('attackCallback', msg="Service Check Succeeded")
        userMsg = "Service Check Succeeded"
    else:
        log.info('attackCallback', msg="Service Check Failed")
        userMsg = "Service Check Failed"
        logs = getLogs(service)
        resultChannel.basic_publish(exchange='resultX',
                                    routing_key=str(service.userInfo),
                                    body=json.dumps({'msg': userMsg, 'logs':logs, 'display':'logs', 'service': service.__dict__}))
        cleanup(service, log)
        ch.basic_ack(delivery_tag = method.delivery_tag)
        return -1

    
    exploitModuleName = 'Exploits.' + service.exploitModule
    exploitModule = importlib.import_module(exploitModuleName, package=None)
    exploitObject = exploitModule.Exploit(service)
    exploitObject.exploit()

    exploitSuccess = exploitObject.exploitSuccess()

    if exploitSuccess:
        userMsg = "Your Code/Config was exploited."
        log.info("attackCallback", msg="Exploit Success")
        resultChannel.basic_publish(exchange='resultX',
                                    routing_key=str(service.userInfo),
                                    body=json.dumps({'msg': userMsg, 'display':'msg', 'service': service.__dict__}))

        cleanup(service, log)
        ch.basic_ack(delivery_tag = method.delivery_tag)
        return -1

    else:
        userMsg = "Attack Failed"
        log.info("attackCallback", msg=userMsg)

    checkService = serviceCheckObject.checkService()

    if not exploitSuccess and checkService:

        log.info('attackCallback', msg="Service Check Succeeded After Attack")
        userMsg = "Service Check Succeeded After Attack"
        resultChannel.basic_publish(exchange='resultX',
                                    routing_key=str(service.userInfo),
                                    body=json.dumps({'msg': userMsg, 'flag': serviceCheckObject.flag, 'display':'flag', 'service': service.__dict__}))

    elif not exploitSuccess and not checkService:
        log.info('attackCallback', msg="Service Check Failed After Attack")
        userMsg = "Service Check Failed After Attack"
        logs = getLogs(service, log)
        resultChannel.basic_publish(exchange='resultX',
                                    routing_key=str(service.userInfo),
                                    body=json.dumps({'msg': userMsg, 'logs':logs, 'display':'logs', 'service': service.__dict__}))

        cleanup(service, log)  
        ch.basic_ack(delivery_tag = method.delivery_tag)
        return -1

    cleanup(service, log)
    ch.basic_ack(delivery_tag = method.delivery_tag)
    return 1

def attackWorker():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='attackQueue', durable=True)
    logger.info("attackWorker", msg="Starting Attack Worker", queue="attackQueue") 
    channel.basic_consume(attackCallback,queue='attackQueue')
    channel.start_consuming()

def startAttackWorkers(numThreads):
    for i in range(numThreads):
        t = Process(target=attackWorker)
        t.daemon = True
        t.start()

