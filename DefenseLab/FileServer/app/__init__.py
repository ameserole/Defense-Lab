from flask import Flask
from flask_cors import CORS

UPLOAD_FOLDER = '/media/DefenseLab'

app = Flask(__name__)
CORS(app)
app.config.from_object('config')

from app import views
