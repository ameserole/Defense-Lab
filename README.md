# Defense-Lab
I need a better name

## Setup
1. Copy `defense-plugin` into the plugins directory under your CTFd folder.
2. Clone `https://github.com/codemirror/CodeMirror` into the `themes/<theme>/static` directory under your CTFd folder.
3. Start CTFd up
4. Start the file server up by going into the `DefenseLab/FileServer` directory and running `python serve.py`
5. Start the Defense Lab up by going into the `DefenseLab/` directory and running `python DefenseLab.py`
6. Enjoy!

## Challenge Creation
1. Under the `DefenseLab/Services` create a new directory with the name of your service.
2. Inside of your new services directory create a `Dockerfile` for your service and include all supporting files needed.
3. Inside of your new services directory create new python source file with the exact same name as the directory you created. This file will be used as the service check module for your new service. For an example of how the source file works refer to the example in `SampleService`.
4. Inside of the `Exploits` create a new python source file with the name of your exploit. In the source file will be the exploit code that will be executed. This code has to follow the Exploit Framework. For an example look at `overwriteLocalVar.py` file.
