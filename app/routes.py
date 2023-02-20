from app import app
from app import video
from flask import send_from_directory, request, jsonify, url_for
from app import tasks


@app.route("/")
def index():
    return "Flask Media Storage Version 0.1"


@app.route("/video", methods=["POST"])
def add_video():
    content = request.json
    task_type = content["type"]
    task = tasks.video_task.delay(int(task_type))
    return (
        jsonify({"tracker": url_for("task_status", uid=task.id)}),
        202,
    )


@app.route("/status/<uid>")
def task_status(uid):
    task = tasks.video_task.AsyncResult(uid)
    print(task.info)

    if task.state == "FAILURE":
        return jsonify({"status": task.state, "error": str(task.info)})

    return jsonify(
        {
            "status": task.state,
            "result": {
                "cover": task.info.get("cover", ""),
                "videos": task.info.get("videos", []),
                "thumbnails": task.info.get("thumbnails", []),
            },
        }
    )


@app.route("/%s/<path:path>" % (app.config["BASE_DIR"]))
def send_file(path):
    return send_from_directory(app.config["BASE_DIR"], path)
