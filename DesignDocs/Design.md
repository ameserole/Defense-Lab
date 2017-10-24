# Design Doc

## Overview:
This lab is designed in order to test a users ability to correctly identify and fix misconfigured config files or insecurely written code.
The user will be given a file or set of files and told that it is vulnerable and that they need to patch/fix it in order to get points. 
The user will be able to submit their fixes through some interface, either uploading files or typing new file. The files submitted will
then be tested inside of the defense lab. The defense lab will start the service being tested using the submitted files. The lab will then
launch an attack against the known vulnerabality in the service. If the attack is not successful and the service is still running correctly
then the user was successful and a flag is awarded.

## Design Drawing
[Design]: https://github.tamu.edu/tamuctf-dev/Defense-Lab/blob/master/DesignDocs/DefenseLabDesing.jpg "Design Drawing"
![Design Picture][Design]

## Fronted

[Frontend Design]: https://github.tamu.edu/tamuctf-dev/Defense-Lab/blob/master/DesignDocs/FrontendSketch.jpg "Frontend Design Drawing"
![Design Picture][Frontend Design]

### Defense Lab Tab
- New tab on CTFd
- Three major sections:
  - Challenge Selector
    - Dropdown menu that allows users to pick which challenge that they are working on
  - Text Editor
    - Integrated text editor that allows the user to edit the challenge file
    - Display file based on what challenge is selected
    - Save and Submit button that uploads the file to the Defense Lab Server and puts service on the service queue
    - Possibly use [http://codemirror.net/](http://codemirror.net/)
  - Results Display
    - Text box that will either display the logs from the failed service or the flag for the challenge

### Challenges Tab
- Add defense lab challenge descriptions
- Add downloadable file or files that are to be fixed

## Backend

### File Server
[File Backend Design]: https://github.tamu.edu/tamuctf-dev/Defense-Lab/blob/master/DesignDocs/FileBackendSketch.jpg "File Backend Design Drawing"
![File Backend Design][File Backend Design]

### Service Framework
- Services
  - Prebuilt Docker images 
  - Load files using attached volumes with the config/source files to tests
  - Start service
- Workers
  - Spawn containers with vulnerable services
  - Pull messages off of queue
    - Files to use
    - Service/Image to use
  - Push message onto attacker queue
    - Host
    - Port
    - Exploit Name
    - Success Check

### Attacking Framework
- Exploit Framework
  - Possible use metasploit if easier and feasable
  - If we write our own small framework it might be easier to use with our specific exploits and could be a better learning experience
  - Treat each exploit as a module
    - Target host
    - Target port
    - Exploit code to run
    - Exploit name
    - Exploit success check code
    - this could be applied to both local and remote exploits... udev privesc example for linux (udev-late-rules)
      - likely to be able to script metasploit usage (or other exploit usage) to trigger upon file update
  - Make it easy to interface with remotely
    - RPC, API, etc
- Workers
  - Have several containers loaded with the exploit framework
  - Pull messages off of the attack queue
    - Each message contains:
      - Target host/port
      - Exploit name
      - Success check method
      - Service check method
  - General attack outline
    - Check service is up
      - Service could have been misconfigured incorrectly and not working from the get go
      - If service is down return failure
    - Attack target host
      - If attack is successfull return failure
    - Check service is still up
      - Just in case the attack still made the service unstable
      - If service is down return failure
    - Retrun success or failure to user
      - If the service has was down return the logs for the user to have for debugging
    - Success means service is still up and the exploit failed
  - Push message onto cleanup queue
  
### Cleanup
- Clean up containers and volumes when done
- Pull messages off of queue
  - Messages contain
    - Container to clean up
    - Volume to clean up
  
