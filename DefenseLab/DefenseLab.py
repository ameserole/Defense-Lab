import structlog
import time
from Services.BuildImages import buildAllImages
from AttackWorkers import startAttackWorkers
from ServiceWorkers import startServiceWorkers
from CleanupWorkers import startCleanupWorkers

logger = structlog.get_logger()

ServiceWorkerNumber = 2
AttackWorkerNumber = 2
CleanupWorkerNumber = 2

logger.info("DefenseLab", msg="Building All Images")
buildAllImages("/home/messy/Defense-Lab/DefenseLab/Services/")

logger.info("DefenseLab", msg="Starting Service Workers", workerNum=ServiceWorkerNumber)
startServiceWorkers(ServiceWorkerNumber)
logger.info("DefenseLab", msg="Starting Attack Workers", workerNum=AttackWorkerNumber)
startAttackWorkers(AttackWorkerNumber)
logger.info("DefenseLab", msg="Starting Cleanup Workers", workerNum=CleanupWorkerNumber)
startCleanupWorkers(CleanupWorkerNumber)

while True:
    time.sleep(60)
