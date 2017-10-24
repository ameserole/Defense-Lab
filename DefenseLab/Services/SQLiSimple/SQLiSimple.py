from .. import ServiceFrame
import requests
import structlog

logger = structlog.get_logger()


class ServiceCheck(ServiceFrame.ServiceFrame):
    def __init__(self, serviceInfo):
        ServiceFrame.ServiceFrame.__init__(self, serviceInfo)
        self.flag = "gigem{sqli_injection}"

    def checkService(self):
        url = "http://{}/login.php".format(self.serviceInfo.serviceHost)
        msg = "Attempting to open {}".format(url)
        logger.info("SQLiSimple", msg=msg, serviceInfo=self.serviceInfo.__dict__)
        try:
            data = { 'username':'bob', 'password':'bobspassword' }
            r = requests.post(url, data=data)
            if r.text != '<html>You logged in as bob</html>':
                msg = "Incorrect Response {}".format(r.text)
                logger.info("SQLiSimple", msg=msg, serviceInfo=self.serviceInfo.__dict__)
                return False
            msg = "Succesfully open {}: {}".format(url, r.text)
            logger.info("SQLiSimple", msg=msg, serviceInfo=self.serviceInfo.__dict__)
            return True

        except:
            msg = "Failed to open {}: {}".format(url, data)
            logger.info("SQLiSimple", msg=msg, serviceInfo=self.serviceInfo.__dict__)
            return False
        return False
