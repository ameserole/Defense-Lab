from DefenseLab.ServiceManager import ServiceInfo, buildImage, startService, cleanupService
import mock
import docker


def test_ServiceInfo():
    fakeInfo = {
        'serviceName': 'fakeName',
        'imageName': 'fakeImage',
        'volumeLocation': 'fakeVolume',
        'serviceHost': '127.0.0.1',
        'servicePort': 80,
        'exploitModule': 'fakeExploit',
        'serviceCheckName': 'fakeCheck',
        'userInfo': 'fakeInfo'}

    service = ServiceInfo(fakeInfo)
    assert service.__dict__ == fakeInfo


def test_buildImage():
    with mock.patch('docker.models.images.ImageCollection.build') as dockerClient:
        buildImage('/fake/path/', 'fakeImage')
        assert dockerClient.called_with(path='/fake/path/', image='fakeImage')


def test_startService(fake_service, fake_container):
    with mock.patch('docker.models.images.ImageCollection.get') as dockerGet, \
            mock.patch('docker.models.containers.ContainerCollection.create') as dockerCreate, \
            mock.patch('docker.api.container.ContainerApiMixin.inspect_container') as dockerInspect, \
            mock.patch('DefenseLab.ServiceManager.cleanupService') as serviceClean:

        dockerGet.return_value = 'image'
        dockerCreate.return_value = fake_container
        dockerInspect.return_value = {'NetworkSettings':
                                      {'Networks':
                                          {'bridge':
                                              {'IPAddress': '172.17.0.2'}
                                           }
                                       }
                                      }
        serviceClean.return_value = True

        service = fake_service
        service = startService(service)
        volume = service.volumeLocation + ':' + service.volumeLocation
        fileloc = "FILELOC=" + service.volumeLocation
        assert dockerGet.called_with(service.imageName)
        assert dockerCreate.called_with('image',
                                        name=service.serviceName,
                                        tty=True,
                                        volumes=[volume],
                                        environment=[fileloc])
        assert dockerInspect.called_with(service.serviceName)
        assert service.serviceHost == '172.17.0.2'


def test_cleanupService(fake_service, fake_container):
    with mock.patch('docker.models.images.ImageCollection.get') as dockerGet:
        dockerGet.return_value = fake_container
        service = fake_service
        cleanupService(service)

        assert dockerGet.called_with(service.serviceName)


def test_cleanupService_error(fake_service):
    with mock.patch('docker.models.images.ImageCollection.get') as dockerGet:
        def side_effect(arg):
            raise Exception(docker.errors.NotFound)

        dockerGet.side_effect = side_effect
        assert not cleanupService(fake_service)
