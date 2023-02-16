from flask import Flask
from config import Config


app = Flask(__name__)
app.config.from_object(Config)
app.static_folder = app.config["BASE_DIR"]

from app import routes
