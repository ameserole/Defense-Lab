import os
basedir = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = '/home/DefenseLab'

MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # Max file size is 1 MB

WFT_CSRF_ENABLED = True
SECRET_KEY = 'password2'
