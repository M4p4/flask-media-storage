from flask import Flask
from config import Config
from celery import Celery


app = Flask(__name__)
app.config.from_object(Config)
app.static_folder = app.config["BASE_DIR"]

celery = Celery(app.name, broker=app.config["CELERY_BROKER_URL"])
celery.conf.update(app.config)

from app import tasks
from app import routes
