from app import app
import cv2
import os
import math
import numpy as np
import random
from PIL import Image


extensions = {"JPG": ".jpg", "PNG": ".png", "WEBP": ".webp"}


def process_video(source):
    thumbnail_config = app.config["IMAGE_SETTINGS"]["THUMBNAIL"]

    source = os.path.join(os.getcwd(), "example2.mp4")

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
    create_cover(cover_screenshot)


def get_video_screenshot(video, frame_number):
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    _, frame = video.read()
    _, img = cv2.imencode(".png", frame)
    return np.array(img).tobytes()


def create_cover(screenshot):
    cover_config = app.config["IMAGE_SETTINGS"]["COVER"]
    final_path = os.path.join(os.getcwd(), cover_config.get("path"))
    filename = "%s%s" % (
        cover_config.get("filename"),
        extensions.get(cover_config.get("extension")),
    )
    create_path(final_path)
    print(final_path)
    print(filename)


def create_path(path: str):
    if not os.path.exists(path):
        os.makedirs(path)
