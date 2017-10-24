# Low Level Design for the Defense Lab

## Frontend
- Still haven't decided :(
- Some file uploading method
	- Paste into console?
	- Web UI?
	- CTFd tab plugin?
	
- ideas
	- for code fixes and configs: can give them the one file that is vulnerable to exploit (ex: php file vuln to RFI/LFI, sql injection, php command injection) just give them a download for the file, then upload the text of the file through web UI/console

## Backend
### Service Framework
- Service
	- Docker Images
		- Have a separate Dockerfile for each service
		- Each Dockerfile will contain the instructions to setup and start the service
			- OS, Makefile, Installs, etc
		- Attach a volume with all the necessary config or source files
	- Class ServiceManager 
		-	Variables:
			- volumeLocation
			- dockerfileLocation
			- container
			- userInfo
			- serviceHost
			- servicePort
			- exploitModuleName
			- serviceCheckName
		- Functions:
			- createContainer()
				- Create container with volume containing user files attached
			- startService()
				- Start container
				- Populate serviceHost and servicePort
			- cleanupService()
				- Delete container
				- Delete attached volume
	- Class ServiceCheck
		- Variables:
			- checkName
			- serviceHost
			- servicePort
		- Functions:
			- checkService()
				- Virtual function to be filled by subclass
				- Check that service is still up
	- ServiceWorker Module
		- Functions:
			- getServiceMessageFromQueue()
				- Pull a message off of the service Queue
				- Place info into a service manager class
			- workerMain()
				- Call service = getServiceMessageFromQueue()
				- Call service.buildImage()
				- Call service.startService()
				- Call placeServiceOnAttackQueue(service)
			- placeServiceOnAttackQueue(service)
				- place all of the service info onto the attack queue 
	- CleanupWorker Module
		- Functions:
			- getCleanupMessageFromQueue()
				- Call service.cleanup()

### Attack Framework
- Exploit Framwork
	- Class ExploitObj
		- Variables:
			- remote exploits
				- Target Host
				- Target Port
				- Exploit Name
			- local exploits
				- target service
				- additional information (ex: for udev, requires udev pid)
		- Functions:
			- exploit()
				- Virtual function
				- Run the actual exploit
			- checkExploitSuccess()
				- Virtual function
				- Check if the exploit was successfull
	- AttackWorker Module
		- Functions:
			- getAttackMessageFromQueue()
				- Pull a message off of the service queue
			- getAttackFromModuleName(service)
				- Return attack module
			- getServiceCheckFromName(service)
				- Return service check module
			- putServiceOnCleanupQueue(service)
				- Put a service onto the cleanup queue
			- workerMain()
				- service = getAttackMessageFromQueue()
				- serviceCheck = getServiceCheck(service)
				- serviceCheck.checkService()
				- exploit = getExploit(service)
				- exploit.exploit()
				- exploit.checkExploitSuccess()
				- serviceCheck.checkService()
				- putServiceOnCleanupQueue(service)
				- Return success or failure
					- check for root# permissions (id == 0) or check if sensitive info is exposed (through sqli), or if other exploits are still viable
 






















