from app import app
import cv2
import os
import math
import numpy as np
import random
import io
from PIL import Image


extensions = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}


def process_video(source):
    thumbnails = []
    videos = []
    cover = None
    try:
        thumbnail_config = app.config["IMAGE_SETTINGS"]["THUMBNAIL"]

        source = os.path.join(os.getcwd(), "example2.mp4")
        video_id = "1337"
        filename = "test"

        video = cv2.VideoCapture(source)

        # video runtime in seconds
        frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = video.get(cv2.CAP_PROP_FPS)
        total_seconds = round(frames / fps)

        # find a smaller amount if video is short
        amount = thumbnail_config.get("amount")
        if total_seconds - 1 < amount:
            amount = total_seconds - 1
            if amount < 1:
                amount = 1

        # get screenshots
        step_size = math.floor(total_seconds / amount)
        screenshots = []
        for i in range(0, amount):
            frame_number = (i + 1) * step_size
            screenshots.append(get_video_screenshot(video, frame_number))
        video.release()

        # cover
        cover_index = random.randint(0, 5 if (amount - 1) >= 5 else (amount - 1))
        cover_screenshot = screenshots[cover_index]
        cover = create_cover(cover_screenshot, video_id, filename)

        # thumbnails
        for i in range(0, amount):
            thumbnails.append(
                create_thumbnail(screenshots[i], video_id, filename, i + 1)
            )

    except Exception as e:
        print(str(e))
        # rollback something went wrong
        delete_file(os.path.join(app.root_path, cover))
        for thumbnail in thumbnails:
            delete_file(os.path.join(app.root_path, thumbnail))
        return None, [], []
    return cover, thumbnails, videos


def get_video_screenshot(video, frame_number):
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    _, frame = video.read()
    _, img = cv2.imencode(".png", frame)
    return np.array(img).tobytes()


def create_thumbnail(screenshot, id: str, filename: str, seq: int):
    thumbnail_config = app.config["IMAGE_SETTINGS"]["THUMBNAIL"]
    thumbnail_path = (
        thumbnail_config.get("path").replace("{ID}", id).replace("{SEQ}", str(seq))
    )

    final_path = os.path.join(
        app.root_path,
        app.config["BASE_DIR"],
        thumbnail_path,
    )
    final_filename = "%s%s" % (
        thumbnail_config.get("filename"),
        extensions.get(thumbnail_config.get("extension")),
    )
    final_filename = final_filename.replace("{FILENAME}", filename)
    final_filename = final_filename.replace("{SEQ}", str(seq))
    create_path(final_path)
    image = Image.open(io.BytesIO(screenshot))
    image.thumbnail((thumbnail_config.get("width"), thumbnail_config.get("height")))
    if thumbnail_config.get("extension") != "PNG":
        image.convert("RGB")
    image.save(
        os.path.join(final_path, final_filename), thumbnail_config.get("extension")
    )
    image.close()
    return os.path.join(
        app.config["BASE_DIR"],
        thumbnail_path,
        final_filename,
    )


def create_cover(screenshot, id: str, filename: str):
    cover_config = app.config["IMAGE_SETTINGS"]["COVER"]
    cover_path = cover_config.get("path").replace("{ID}", id)
    final_path = os.path.join(
        app.root_path,
        app.config["BASE_DIR"],
        cover_path,
    )
    final_filename = "%s%s" % (
        cover_config.get("filename"),
        extensions.get(cover_config.get("extension")),
    )
    final_filename = final_filename.replace("{FILENAME}", filename)
    create_path(final_path)
    image = Image.open(io.BytesIO(screenshot))
    image.thumbnail((cover_config.get("width"), cover_config.get("height")))
    if cover_config.get("extension") != "PNG":
        image.convert("RGB")
    image.save(os.path.join(final_path, final_filename), cover_config.get("extension"))
    image.close()
    return os.path.join(app.config["BASE_DIR"], cover_path, final_filename)


def create_path(path: str):
    if not os.path.exists(path):
        os.makedirs(path)


def delete_file(path):
    try:
        if os.path.isfile(path):
            os.remove(path)
            return True
    except Exception as e:
        print(str(e))
        return False
    return False
