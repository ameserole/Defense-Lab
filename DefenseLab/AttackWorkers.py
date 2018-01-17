import importlib
import json
import structlog
import pika
import config
from multiprocessing import Process
from ServiceManager import ServiceInfo, getLogs

logger = structlog.get_logger()


def cleanup(service, log):
    """Puts service onto cleanup queueu"""

    connection = pika.BlockingConnection(pika.ConnectionParameters(config.RABBITMQ_SERVER))
    channel = connection.channel()
    channel.queue_declare(queue='cleanupQueue', durable=True)
    channel.basic_publish(exchange='',
                          routing_key='cleanupQueue',
                          body=json.dumps(service.__dict__))

    log.info("attackCallback", msg="Attack Done")


def attackCallback(ch, method, properties, body):
    """Pull service off of attack queue and run selected attack against it"""

    connection2 = pika.BlockingConnection(pika.ConnectionParameters(config.RABBITMQ_SERVER))
    resultChannel = connection2.channel()
    resultChannel.exchange_declare(exchange='resultX', exchange_type='direct')
    resultChannel.queue_declare(queue='resultQueue', durable=True)

    body = json.loads(body)
    logger.info("attackCallback", msg="Recieved Message", body=body)
    service = ServiceInfo(body)

    # Queue for users to reviece the results
    resultChannel.queue_bind(exchange='resultX', queue='resultQueue', routing_key=str(service.userInfo))

    log = logger.bind(service=service.__dict__)
    userMsg = "Starting Attack on {}\n".format(service.serviceName)

    # Get the Service module for this service and check that it is running correctly
    serviceCheckModuleName = 'DefenseLab.Services.' + service.serviceCheckName + '.' + service.serviceCheckName
    serviceModule = importlib.import_module(serviceCheckModuleName, package=None)
    serviceCheckObject = serviceModule.ServiceCheck(service)

    if serviceCheckObject.checkService():
        log.info('attackCallback', msg="Service Check Succeeded")
        userMsg = "Service Check Succeeded"
    else:
        log.info('attackCallback', msg="Service Check Failed")
        userMsg = "Service Check Failed"
        logs = serviceCheckObject.getLogs()
        resultChannel.basic_publish(exchange='resultX',
                                    routing_key=str(service.userInfo),
                                    body=json.dumps({'msg': userMsg, 'logs': logs, 'display': 'logs', 'service': service.__dict__}))
        cleanup(service, log)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return -1

    # If the service is running correctly grab the selected exploit module and run it against the current service
    exploitModuleName = 'DefenseLab.Exploits.' + service.exploitModule
    exploitModule = importlib.import_module(exploitModuleName, package=None)
    exploitObject = exploitModule.Exploit(service)
    exploitObject.exploit()

    exploitSuccess = exploitObject.exploitSuccess()

    if exploitSuccess:
        userMsg = "Your Code/Config was exploited."
        log.info("attackCallback", msg="Exploit Success")
        resultChannel.basic_publish(exchange='resultX',
                                    routing_key=str(service.userInfo),
                                    body=json.dumps({'msg': userMsg, 'display': 'msg', 'service': service.__dict__}))

        cleanup(service, log)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return -1

    else:
        userMsg = "Attack Failed"
        log.info("attackCallback", msg=userMsg)

    # Check to see if the service is still up after the exploit was run
    checkService = serviceCheckObject.checkService()

    # If Service is still up and exploit did not work return the flag to the user
    if not exploitSuccess and checkService:
        log.info('attackCallback', msg="Service Check Succeeded After Attack")
        userMsg = "Service Check Succeeded After Attack"
        resultChannel.basic_publish(exchange='resultX',
                                    routing_key=str(service.userInfo),
                                    body=json.dumps({'msg': userMsg, 'flag': serviceCheckObject.flag, 'display': 'flag', 'service': service.__dict__}))

    # No flag for you :(
    elif not exploitSuccess and not checkService:
        log.info('attackCallback', msg="Service Check Failed After Attack")
        userMsg = "Service Check Failed After Attack"
        logs = getLogs(service, log)
        resultChannel.basic_publish(exchange='resultX',
                                    routing_key=str(service.userInfo),
                                    body=json.dumps({'msg': userMsg, 'logs': logs, 'display': 'logs', 'service': service.__dict__}))

        cleanup(service, log)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return -1

    cleanup(service, log)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    return 1


def attackWorker():
    """Declare attack queue and callback function"""
    connection = pika.BlockingConnection(pika.ConnectionParameters(config.RABBITMQ_SERVER))
    channel = connection.channel()
    channel.queue_declare(queue='attackQueue', durable=True)
    logger.info("attackWorker", msg="Starting Attack Worker", queue="attackQueue")
    channel.basic_consume(attackCallback, queue='attackQueue')
    channel.start_consuming()


def startAttackWorkers(numThreads):
    """Start up numThreads attack workers"""
    for i in range(numThreads):
        t = Process(target=attackWorker)
        t.daemon = True
        t.start()
