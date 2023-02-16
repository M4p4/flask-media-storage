from app import app
from app import video


@app.route("/")
def index():
    id = "1337"
    video.process_video("")
    return "Hello World!"
