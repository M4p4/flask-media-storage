from app import app
from flask import send_from_directory, request, jsonify
from app import tasks
import os
from werkzeug.utils import secure_filename
from app import helper
from functools import wraps
import validators


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
    return "Flask Media Storage Version 0.3"


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
    download_url = True
    if not request.form.get("url"):
        download_url = False

    if not download_url and request.files["file"].filename == "":
        return jsonify({"error": "file or url is required."}), 400

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
    if download_url:
        url = request.form.get("url")
        if not validators.url(url):
            return jsonify({"error": "invalid url"}), 400
        tmp_file = url
        if not helper.validate_file_extension(tmp_file, media_type):
            return jsonify({"error": "url format not supported"}), 400
        file_extension = helper.get_file_extension(tmp_file)
    else:
        file = request.files["file"]
        if not helper.validate_file_extension(file.filename, media_type):
            return jsonify({"error": "format not supported"}), 400

        filename = secure_filename(file.filename)
        tmp_path = os.path.join(app.root_path, app.config["BASE_DIR"], "tmp")
        helper.create_path(tmp_path)
        tmp_file = os.path.join(tmp_path, f"{helper.get_uuid()}_{filename}")
        file.save(tmp_file)
        file_extension = helper.get_file_extension(filename)

    settings = {
        "id": str(request.form.get("id")),
        "filename": request.form.get("filename"),
        "use_watermark": request.form.get("use_watermark") == "True"
        or request.form.get("use_watermark") == "true"
        or request.form.get("use_watermark") == "1",
        "watermark_text": request.form.get("watermark_text", ""),
        "rid": helper.get_random_id(app.config["RANDOM_ID_LEN"]),
        "download_url": download_url,
        "file_extension": file_extension,
    }

    task = (
        tasks.video_task.delay(tmp_file, settings)
        if media_type == "video"
        else tasks.image_task.delay(tmp_file, settings)
    )

    return (
        jsonify(
            {
                "media_id": task.id,
                "download_url": download_url,
            }
        ),
        202,
    )


@app.route("/status/<uid>")
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
