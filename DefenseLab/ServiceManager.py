import docker
import structlog
import time

logger = structlog.get_logger()
WAIT_TIME = 5

client = docker.from_env(version="auto")

class ServiceInfo(object):
    def __init__(self, info):
        self.serviceName = info['serviceName']
        self.imageName = info['imageName']
        self.volumeLocation = info['volumeLocation']
        self.serviceHost = info['serviceHost'] 
        self.servicePort = info['servicePort']
        self.exploitModule = info['exploitModule']
        self.serviceCheckName = info['serviceCheckName']
        self.userInfo = info['userInfo']


def buildImage(dockerRoot, imageName):
    logger.info("buildImage", imageName=imageName, dockerRoot=dockerRoot)
    image = client.images.build(path=dockerRoot, tag=imageName)

def startService(serviceInfo):
    logger.info("startService", service=serviceInfo.__dict__)
    cleanupService(serviceInfo)
    image = client.images.get(serviceInfo.imageName)  
    portNum = serviceInfo.servicePort
    ports = {portNum: portNum}
    fileloc = "FILELOC="+serviceInfo.volumeLocation
    volume = serviceInfo.volumeLocation+':'+serviceInfo.volumeLocation
    container =  client.containers.create(
                                    image, 
                                    name=serviceInfo.serviceName,
                                    tty=True,
                                    volumes=[volume],
                                    environment=[fileloc]
                                    
                                  )
    container.start()
    time.sleep(WAIT_TIME)
    logger.info("startService", msg="Service Started", serviceInfo=serviceInfo.__dict__)
    apiclient = docker.APIClient(version="auto")
    serviceInfo.serviceHost =  apiclient.inspect_container(serviceInfo.serviceName)['NetworkSettings']['Networks']['bridge']['IPAddress']
    logger.info("startService", serviceInfo=serviceInfo.__dict__, logs=container.logs(stdout=True, stderr=True))
    
    return serviceInfo

def getLogs(serviceInfo):
    try:
        container = client.containers.get(serviceInfo.serviceName)
        return container.logs(stdout=True, stderr=True)
    except:
        return ""
    
def cleanupService(serviceInfo):
    logger.info("cleanupService", serviceInfo=serviceInfo.__dict__)
    try:
        container = client.containers.get(serviceInfo.serviceName)
        container.stop()
        container.remove()
    except docker.errors.NotFound:
        logger.error("cleanupService", msg="Container Not Found", serviceInfo=serviceInfo.__dict__)
        pass
