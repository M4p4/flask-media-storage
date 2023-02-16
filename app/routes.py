from app import app
from app import video
from flask import send_from_directory


@app.route("/")
def index():
    id = "1337"
    video.process_video("")
    return "Flask Media Storage Version 0.1"


@app.route("/%s/<path:path>" % (app.config["BASE_DIR"]))
def send_file(path):
    return send_from_directory(app.config["BASE_DIR"], path)
