from app import app
from flask import send_from_directory, request, jsonify
from app import tasks
import os
from werkzeug.utils import secure_filename
from app import helper
from functools import wraps


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not request.form.get("auth"):
            return jsonify({"error": "please provide a auth key"}), 400

        if request.form.get("auth") != app.config["AUTH_KEY"]:
            return jsonify({"error": "invalid auth key"}), 400
        return f(*args, **kwargs)

    return decorated


@app.route("/")
def index():
    return "Flask Media Storage Version 0.2"


@app.route("/video/<uid>", methods=["DELETE"])
@auth_required
def delete_video(uid):
    task = tasks.video_task.AsyncResult(uid)
    if task.state == "SUCCESS":
        files = []
        files.append(task.info.get("cover", None))
        videos = task.info.get("videos", [])
        for video in videos:
            files.append(video)
        thumbnails = task.info.get("thumbnails", [])
        for thumbnail in thumbnails:
            files.append(thumbnail)
        deleted_files = 0
        for file in files:
            if helper.delete_file(os.path.join(app.root_path, file)):
                deleted_files += 1
        return jsonify(
            {
                "status": "success",
                "deleted_files": deleted_files,
                "submitted_files": len(files),
            }
        )
    return jsonify({"status": "error", "message": "invalid task id"})


@app.route("/image/<uid>", methods=["DELETE"])
@auth_required
def delete_image(uid):
    task = tasks.video_task.AsyncResult(uid)
    if task.state == "SUCCESS":
        deleted_files = 0
        if task.info.get("image", None) != None and helper.delete_file(
            os.path.join(app.root_path, task.info.get("image", None))
        ):
            deleted_files += 1
        if task.info.get("thumbnail", None) != None and helper.delete_file(
            os.path.join(app.root_path, task.info.get("thumbnail", None))
        ):
            deleted_files += 1
        return jsonify(
            {
                "status": "success",
                "deleted_files": deleted_files,
                "submitted_files": 2,
            }
        )
    return jsonify({"status": "error", "message": "invalid task id"})


@app.route("/media", methods=["POST"])
@auth_required
def add_media():
    if request.files["file"].filename == "":
        return jsonify({"error": "file is required."}), 400

    file = request.files["file"]

    if not request.form.get("id"):
        return jsonify({"error": "id is required"}), 400

    if not request.form.get("filename"):
        return jsonify({"error": "filename is required"}), 400

    if not request.form.get("media_type"):
        return jsonify({"error": "mediatype is required"}), 400

    if (
        request.form.get("media_type") != "video"
        and request.form.get("media_type") != "image"
    ):
        return jsonify({"error": "mediatype is invalid (image and video only)"}), 400

    media_type = request.form.get("media_type")
    point_split = file.filename.split(".")
    extension = point_split[len(point_split) - 1]
    if (
        media_type == "video"
        and extension not in app.config["ALLOWED_VIDEO_EXTENSIONS"]
    ) or (
        media_type == "image"
        and extension not in app.config["ALLOWED_IMAGE_EXTENSIONS"]
    ):
        return jsonify({"error": "format not supported"}), 400

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
        "rid": helper.get_random_id(app.config["RANDOM_ID_LEN"]),
    }

    task = (
        tasks.video_task.delay(tmp_file, settings)
        if media_type == "video"
        else tasks.image_task.delay(tmp_file, settings)
    )

    return (
        jsonify({"media_id": task.id}),
        202,
    )


@app.route("/status/<uid>")
@auth_required
def task_status(uid):
    task = tasks.video_task.AsyncResult(uid)

    if task.state == "FAILURE":
        return jsonify({"status": task.state, "error": str(task.info), "media_id": uid})

    if task.state == "SUCCESS":
        result = (
            (
                {
                    "cover": task.info.get("cover", ""),
                    "videos": task.info.get("videos", []),
                    "thumbnails": task.info.get("thumbnails", []),
                },
            )
            if task.info.get("file_type") == "video"
            else (
                {
                    "thumbnail": task.info.get("thumbnail", ""),
                    "image": task.info.get("image", []),
                },
            )
        )

        return jsonify(
            {
                "status": task.state,
                "file_type": task.info.get("file_type", "video"),
                "media_id": uid,
                "result": result,
            }
        )

    return jsonify({"status": task.state})


@app.route("/%s/<path:path>" % (app.config["BASE_DIR"]))
def send_file(path):
    return send_from_directory(app.config["BASE_DIR"], path)
