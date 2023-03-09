import os
import shutil
import string
import random
import uuid
from app import app
import requests


def create_path(path: str):
    if not os.path.exists(path):
        os.makedirs(path)


def delete_directory(path: str | None):
    try:
        if path is None:
            return True
        dir_path = os.path.dirname(os.path.abspath(path))
        shutil.rmtree(dir_path)
        return True
    except Exception as e:
        print(str(e))
        return False


def delete_file(path: str | None):
    try:
        if path is None:
            return True
        if os.path.isfile(path):
            os.remove(path)
            return True
    except Exception as e:
        print(str(e))
        return False
    return False


def get_random_id(length: int):
    letters = string.ascii_lowercase + string.digits
    return "".join(random.choice(letters) for i in range(length))


def get_uuid():
    return uuid.uuid1()


def get_file_extension(filename: str):
    point_split = filename.split(".")
    extension = point_split[len(point_split) - 1]
    if extension.find("?") != -1:
        extension = extension[0 : extension.find("?")]
    return extension


def validate_file_extension(filename: str, media_type: str):
    extension = get_file_extension(filename)
    if (
        media_type == "video"
        and extension not in app.config["ALLOWED_VIDEO_EXTENSIONS"]
    ) or (
        media_type == "image"
        and extension not in app.config["ALLOWED_IMAGE_EXTENSIONS"]
    ):
        return False
    return True


def download_file(url: str):
    tmp_path = os.path.join(app.root_path, app.config["BASE_DIR"], "tmp")
    filename = f"{get_uuid()}.{get_file_extension(url)}"
    final_path = os.path.join(tmp_path, filename)
    with requests.get(url, stream=True) as r:
        with open(final_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return final_path
