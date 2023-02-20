from app import app
from flask import send_from_directory, request, jsonify, url_for
from app import tasks
import os
from werkzeug.utils import secure_filename
from app import helper


@app.route("/")
def index():
    return "Flask Media Storage Version 0.2"


@app.route("/video", methods=["POST"])
def add_video():
    file = request.files["file"]
    if request.files["file"].filename == "":
        return jsonify({"error": "file is required."}), 400

    point_split = file.filename.split(".")
    extension = point_split[len(point_split) - 1]
    if extension != "mp4" and extension != "mov":
        return jsonify({"error": "format not supported"}), 400

    if not request.form.get("id"):
        return jsonify({"error": "id is required"}), 400

    if not request.form.get("filename"):
        return jsonify({"error": "filename is required"}), 400

    filename = secure_filename(file.filename)
    tmp_path = os.path.join(app.root_path, app.config["BASE_DIR"], "tmp")
    helper.create_path(tmp_path)
    tmp_file = os.path.join(tmp_path, f"{helper.get_uuid()}_{filename}")
    file.save(tmp_file)
    settings = {
        "id": str(request.form.get("id")),
        "filename": request.form.get("filename"),
        "use_watermark": request.form.get("use_watermark", False, type=bool),
        "watermark_text": request.form.get("watermark_text", ""),
    }
    task = tasks.video_task.delay(tmp_file, settings)
    return (
        jsonify({"tracker": url_for("task_status", uid=task.id)}),
        202,
    )


@app.route("/status/<uid>")
def task_status(uid):
    task = tasks.video_task.AsyncResult(uid)

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
