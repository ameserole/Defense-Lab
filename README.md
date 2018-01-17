# Defense-Lab
I need a better name

Automated secure coding/config testing framework that runs custom attacks against docker containers running services using user/player supplied code.  
This is the original implemenation intended for TAMUctf however it has now evolved beyond this form. I decided to go ahead and implement a small CLI and release the code though.

## Setup
1. Run `./setup.sh` to install all dependencies.
2. Modify `config.py` if needed

## DefenseCLI.py
The command line interface allows you to start the defense lab up and to send messages directly to the queues.
```
$ ./DefenseCLI.py -h
usage: DefenseCLI.py [-h] {start,send} ...

Command Line Interface for Defense Lab

optional arguments:
  -h, --help    show this help message and exit

Lab Commands:
  Commands to start and interact with Defense Lab

  {start,send}  Commands to start and interact with Defense Lab
    start       Start up the defense lab
```
```
$ ./DefenseCLI.py start -h
usage: DefenseCLI.py start [-h] [-wa ATTACK_WORKERS] [-ws SERVICE_WORKERS]
                           [-wc CLEANUP_WORKERS]

Start up the defense lab

optional arguments:
  -h, --help            show this help message and exit
  -wa ATTACK_WORKERS, --attack-workers ATTACK_WORKERS
                        Number of attack workers to start with. Default is
                        two.
  -ws SERVICE_WORKERS, --service-workers SERVICE_WORKERS
                        Number of service workers to start with. Default is
                        two.
  -wc CLEANUP_WORKERS, --cleanup-workers CLEANUP_WORKERS
                        Number of cleanup workers to start with. Default is
                        two.
```
```
$ ./DefenseCLI.py send -h
usage: DefenseCLI.py send [-h] -s SERVICE_NAME -i IMAGE_NAME -v VOLUME -e
                          EXPLOIT -c SERVICE_CHECK -p PORT

Info to push onto the service queue

optional arguments:
  -h, --help            show this help message and exit
  -s SERVICE_NAME, --service-name SERVICE_NAME
                        Name of docker container to create
  -i IMAGE_NAME, --image-name IMAGE_NAME
                        Name of docker image to use
  -v VOLUME, --volume VOLUME
                        Location of files to test
  -e EXPLOIT, --exploit EXPLOIT
                        Name of exploit module to use
  -c SERVICE_CHECK, --service-check SERVICE_CHECK
                        Name of service check module to use
  -p PORT, --port PORT  Port number of service
```

## Example Usage
### Starting with 3 service workers
```
$ ./DefenseCLI.py start -ws 3
2018-01-16 18:23.31 DefenseLab                     msg=Building All Images
2018-01-16 18:23.31 buildAllImages                 dockerRoot=/home/DefenseLab/DefenseLab/Services/ serviceName=apachedirectorytraversal
2018-01-16 18:23.31 buildImage                     dockerRoot=/home/DefenseLab/DefenseLab/Services/ApacheDirectoryTraversal imageName=apachedirectorytraversal
2018-01-16 18:23.31 buildAllImages                 dockerRoot=/home/DefenseLab/DefenseLab/Services/ serviceName=sampleservice
2018-01-16 18:23.31 buildImage                     dockerRoot=/home/DefenseLab/DefenseLab/Services/SampleService imageName=sampleservice
2018-01-16 18:23.31 buildAllImages                 dockerRoot=/home/DefenseLab/DefenseLab/Services/ serviceName=buffintover
2018-01-16 18:23.31 buildImage                     dockerRoot=/home/DefenseLab/DefenseLab/Services/BuffIntOver imageName=buffintover
2018-01-16 18:23.31 buildAllImages                 dockerRoot=/home/DefenseLab/DefenseLab/Services/ serviceName=sqlisimple
2018-01-16 18:23.31 buildImage                     dockerRoot=/home/DefenseLab/DefenseLab/Services/SQLiSimple imageName=sqlisimple
2018-01-16 18:23.31 DefenseLab                     msg=Starting Service Workers workerNum=3
2018-01-16 18:23.31 DefenseLab                     msg=Starting Attack Workers workerNum=2
2018-01-16 18:23.31 DefenseLab                     msg=Starting Cleanup Workers workerNum=2
2018-01-16 18:23.32 serviceWorker                  msg=Starting Service Worker queue=serviceQueue
2018-01-16 18:23.32 serviceWorker                  msg=Starting Service Worker queue=serviceQueue
2018-01-16 18:23.32 serviceWorker                  msg=Starting Service Worker queue=serviceQueue
2018-01-16 18:23.32 attackWorker                   msg=Starting Attack Worker queue=attackQueue
2018-01-16 18:23.32 cleanupWorker                  msg=Starting Cleanup Worker queue=cleanupQueue
2018-01-16 18:23.32 attackWorker                   msg=Starting Attack Worker queue=attackQueue
2018-01-16 18:23.32 cleanupWorker                  msg=Starting Cleanup Worker queue=cleanupQueue

```
### Running an attack attack against a vulnerable service
Vulnerable apache server config:
```
$ ./DefenseCLI.py send -s asdf -i apachedirectorytraversal -v /home/DefenseLab/test/ -e DirectoryTraversal -c ApacheDirectoryTraversal -p 80
  
Pushing: {'serviceCheckName': 'ApacheDirectoryTraversal', 'serviceName': 'asdf', 'exploitModule': 'DirectoryTraversal', 'volumeLocation': '/home/DefenseLab/test/', 'serviceHost': None, 'imageName': 'apachedirectorytraversal', 'userInfo': u'1f4f464dbbfb1562b18cd18123f74d6bece2f6f652a449d7a39719aa50872eb8', 'servicePort': 80}
Waiting for result
{"msg": "Your Code/Config was exploited.", "display": "msg", "service": {"exploitModule": "DirectoryTraversal", "imageName": "apachedirectorytraversal", "servicePort": 80, "serviceCheckName": "ApacheDirectoryTraversal", "serviceName": "asdf", "serviceHost": "172.17.0.2", "volumeLocation": "/home/DefenseLab/test/", "userInfo": "1f4f464dbbfb1562b18cd18123f74d6bece2f6f652a449d7a39719aa50872eb8"}}
```

### Running an attack against a hardened service
Fixed apache server config from last example:
```
$ ./DefenseCLI.py send -s asdf -i apachedirectorytraversal -v /home/DefenseLab/test/ -e DirectoryTraversal -c ApacheDirectoryTraversal -p 80

Pushing: {'serviceCheckName': 'ApacheDirectoryTraversal', 'serviceName': 'asdf', 'exploitModule': 'DirectoryTraversal', 'volumeLocation': '/home/DefenseLab/test/', 'serviceHost': None, 'imageName': 'apachedirectorytraversal', 'userInfo': u'4f6f196f80f59ad2f94b75806f69f4eefe9b38890e2407dc4399bb45d9f3a63e', 'servicePort': 80}
Waiting for result
{"msg": "Service Check Succeeded After Attack", "flag": "gigem{apache_traversal}", "display": "flag", "service": {"exploitModule": "DirectoryTraversal", "imageName": "apachedirectorytraversal", "servicePort": 80, "serviceCheckName": "ApacheDirectoryTraversal", "serviceName": "asdf", "serviceHost": "172.17.0.2", "volumeLocation": "/home/DefenseLab/test/", "userInfo": "4f6f196f80f59ad2f94b75806f69f4eefe9b38890e2407dc4399bb45d9f3a63e"}}
```

## Challenge Creation
1. Under the `DefenseLab/Services` create a new directory with the name of your service.
2. Inside of your new services directory create a `Dockerfile` for your service and include all supporting files needed.
3. Inside of your new services directory create new python source file with the exact same name as the directory you created. This file will be used as the service check module for your new service. For an example of how the source file works refer to the example in `SampleService`.
4. Inside of the `Exploits` create a new python source file with the name of your exploit. In the source file will be the exploit code that will be executed. This code has to follow the Exploit Framework. For an example look at `overwriteLocalVar.py` file.


