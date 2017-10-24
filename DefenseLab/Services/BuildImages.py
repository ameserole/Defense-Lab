import docker
import os
import structlog

client = docker.from_env(version="auto")
logger = structlog.get_logger()

def buildImage(dockerRoot, imageName):
    logger.info("buildImage", imageName=imageName, dockerRoot=dockerRoot)
    image = client.images.build(path=dockerRoot, tag=imageName)

def buildAllImages(serviceDir):
    services = [service for service in os.listdir(serviceDir) 
                if os.path.isdir(os.path.join(serviceDir, service))]
    dockerRoot = serviceDir
    for service in services:
        serviceName = service.lower()
        logger.info("buildAllImages", serviceName=serviceName, dockerRoot=dockerRoot)
        buildImage(dockerRoot+service, serviceName)

if __name__ == '__main__':
    buildAllImages("/home/messy/Documents/Defense-lab/DefenseLab/Services/")
