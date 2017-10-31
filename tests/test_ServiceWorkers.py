import mock
import json
from DefenseLab.ServiceManager import ServiceInfo
from DefenseLab.ServiceWorkers import serviceCallback


def test_serviceCallback(fake_ch, fake_method):
    fakeInfo = {
        'serviceName': 'fakeName',
        'imageName': 'fakeImage',
        'volumeLocation': 'fakeVolume',
        'serviceHost': '127.0.0.1',
        'servicePort': 80,
        'exploitModule': 'fakeExploit',
        'serviceCheckName': 'fakeCheck',
        'userInfo': 'fakeInfo'}

    ch = fake_ch
    method = fake_method
    properties = ""
    body = json.dumps(fakeInfo)
    with mock.patch('pika.channel.Channel.basic_publish') as pikaPub, \
            mock.patch('DefenseLab.ServiceWorkers.startService') as fakeService:

        fakeService.return_value = ServiceInfo(fakeInfo)
        serviceCallback(ch, method, properties, body)
        assert pikaPub.called_with(exchange='',
                                   routing_key='attackQueue',
                                   body=json.dumps(fakeInfo))
