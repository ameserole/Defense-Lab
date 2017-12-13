import structlog
import time
import config
from Services.BuildImages import buildAllImages
from AttackWorkers import startAttackWorkers
from ServiceWorkers import startServiceWorkers
from CleanupWorkers import startCleanupWorkers


logger = structlog.get_logger()

ServiceWorkerNumber = config.NUM_SERVICE_WORKERS
AttackWorkerNumber = config.NUM_SERVICE_WORKERS
CleanupWorkerNumber = config.NUM_CLEANUP_WORKERS

logger.info("DefenseLab", msg="Building All Images")
buildAllImages(config.SERVICE_PATH)

logger.info("DefenseLab", msg="Starting Service Workers", workerNum=ServiceWorkerNumber)
startServiceWorkers(ServiceWorkerNumber)
logger.info("DefenseLab", msg="Starting Attack Workers", workerNum=AttackWorkerNumber)
startAttackWorkers(AttackWorkerNumber)
logger.info("DefenseLab", msg="Starting Cleanup Workers", workerNum=CleanupWorkerNumber)
startCleanupWorkers(CleanupWorkerNumber)

while True:
    time.sleep(60)
