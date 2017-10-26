import os
from app import app
from flask import request, Response
from werkzeug.utils import secure_filename
import pika
import json


def mapChallengeToInfo(challenge):
    return {
        'DefenseLab_Example': ('apachedirectorytraversal', 'DirectoryTraversal', 'ApacheDirectoryTraversal', 80, 'apache2.conf'),
        'DefenseLab_Example2': ('apachedirectorytraversal', 'DirectoryTraversal', 'ApacheDirectoryTraversal', 80, 'apache2.conf'),
        'Can_you_SQL_the_problem': ('sqlisimple', 'SQLi', 'SQLiSimple', 80, 'login.php'),
    }[challenge]


def pushService(sent, folderpath):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='serviceQueue', durable=True)
    challenge = secure_filename(sent['challenge'])
    info = mapChallengeToInfo(challenge)
    serviceName = info[0] + sent['user'].lower()
    service = {
        'serviceName': serviceName,
        'imageName': info[0],
        'volumeLocation': folderpath,
        'userInfo': sent['user'],
        'exploitModule': info[1],
        'serviceCheckName': info[2],
        'serviceHost': None,
        'servicePort': info[3]
    }

    print "Pushing: {}".format(service)
    channel.basic_publish(exchange='',
                          routing_key='serviceQueue',
                          body=json.dumps(service))


@app.route('/upload', methods=["POST", "OPTIONS"])
def upload():
    if request.method == "OPTIONS":
        return ""
    if request.method == "POST":
        sent = request.get_json(force=True)
        print "Recieved: {}".format(sent)

        user = secure_filename(sent['user'])
        chal = secure_filename(sent['challenge'])
        filename = mapChallengeToInfo(chal)[4]
        uploadedfile = sent['file']
        upload_folder = app.config['UPLOAD_FOLDER']
        folderpath = "{}/{}/{}/".format(upload_folder, user, chal)

        if not os.path.exists(folderpath):
            os.makedirs(folderpath)

        filepath = folderpath + filename
        with open(filepath, 'w') as f:
            f.write(uploadedfile)

        pushService(sent, folderpath)

        def generate(teamid):
            connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            userChannel = connection.channel()
            userChannel.exchange_declare(exchange='resultX')
            i = 0
            while i < 1:
                method_frame, header_frame, body = userChannel.basic_get('resultQueue')
                if method_frame:
                    if json.loads(body)['service']['userInfo'] == str(teamid):
                        message = json.loads(body)
                        yield message[message['display']]
                        userChannel.basic_ack(delivery_tag=method_frame.delivery_tag)
                        i += 1
                        break

        return Response(generate(user), mimetype='text/html')

    return ""


@app.route('/<challenge>', methods=["GET"])
def getFile(challenge):
    challenge_name = secure_filename(challenge)
    file_get = mapChallengeToInfo(challenge_name)[4]
    upload_folder = app.config['UPLOAD_FOLDER']
    filepath = "{}/{}".format(upload_folder, file_get)
    with open(filepath, 'r') as f:
        ret_file = f.read()

    return ret_file
