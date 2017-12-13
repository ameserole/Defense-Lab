import os
basedir = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # Max file size is 1 MB

WFT_CSRF_ENABLED = True
SECRET_KEY = 'password2'
