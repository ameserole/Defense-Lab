from .. import ServiceFrame

import structlog

logger = structlog.get_logger()


class ServiceCheck(ServiceFrame.ServiceFrame):
    def __init__(self, serviceInfo):
        ServiceFrame.ServiceFrame.__init__(self, serviceInfo)
        self.flag = "gigem{buffer_int_overflow}"

    def checkService(self):
        pass

    def getLogs(self):
        pass
