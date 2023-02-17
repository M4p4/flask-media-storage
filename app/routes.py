from app import app
from app import video
from flask import send_from_directory


@app.route("/")
def index():
    video_id = 1337
    filename = "test"
    settings = {
        "id": str(video_id),
        "filename": filename,
        "use_watermark": True,
        "watermark_text": "watermark.com",
    }
    cover, thumbnails, videos = video.process_video("", settings)
    print("JOB DONE")
    print(cover)
    print(videos)
    return "Flask Media Storage Version 0.1"


@app.route("/%s/<path:path>" % (app.config["BASE_DIR"]))
def send_file(path):
    return send_from_directory(app.config["BASE_DIR"], path)
