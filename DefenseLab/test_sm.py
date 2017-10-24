from ServiceManager import ServiceInfo as SI
from ServiceManager import buildImage, startService, cleanupService

sm = SI("MyApache")
dockerfile = "/home/messy/Documents/tamuctf-dev/Defense-Lab/DefenseLab"
sm.imageName = "apache-test2"
buildImage(dockerfile, sm.imageName)
startService(sm)
cleanupService(sm)
