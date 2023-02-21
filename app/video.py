from app import app
import cv2
import os
import math
import numpy as np
import random
import io
from PIL import Image
import moviepy.editor as mp
import ffmpeg
from app import helper


extensions = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}
dimensions = {
    "1080": (1920, 1080, 1.2),
    "720": (1280, 720, 1.0),
    "480": (854, 480, 0.7),
    "360": (480, 360, 0.5),
}


def process_video(source, settings):
    thumbnails = []
    videos = []
    cover = None
    audio_temp_file = None
    try:
        thumbnail_config = app.config["IMAGE_SETTINGS"]["THUMBNAIL"]
        video_config = app.config["VIDEO_SETTINGS"]
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
        cover = create_cover(cover_screenshot, settings)

        # thumbnails
        for i in range(0, amount):
            thumbnails.append(create_thumbnail(screenshots[i], settings, i + 1))

        # audio
        audio_temp_file = create_temporay_audio_file(source)

        # videos
        for video_dimensions in video_config.get("formats"):
            video_path = create_video(
                source, audio_temp_file, dimensions.get(str(video_dimensions)), settings
            )
            if video_path:
                videos.append(video_path)
        helper.delete_file(audio_temp_file)
        helper.delete_file(source)

    except Exception as e:
        print(str(e))
        # rollback something went wrong
        helper.delete_file(source)
        helper.delete_directory(os.path.join(app.root_path, cover))
        if len(thumbnails) > 0:
            helper.delete_directory(os.path.join(app.root_path, thumbnails[0]))
        if len(videos) > 0:
            helper.delete_directory(os.path.join(app.root_path, videos[0]))
        if audio_temp_file:
            helper.delete_directory(audio_temp_file)
        return None, [], []
    return cover, thumbnails, videos


def create_video(video, audio, video_dimensions, settings):
    video_config = app.config["VIDEO_SETTINGS"]
    video_path = (
        video_config.get("path")
        .replace("{ID}", settings.get("id"))
        .replace("{FORMAT}", str(video_dimensions[1]))
        .replace("{RID}", settings.get("rid"))
    )
    final_path = os.path.join(
        app.root_path,
        app.config["BASE_DIR"],
        video_path,
    )
    helper.create_path(final_path)
    final_filename = "%s%s" % (
        video_config.get("filename"),
        ".mp4",
    )
    final_filename = (
        final_filename.replace("{FILENAME}", settings.get("filename"))
        .replace("{ID}", settings.get("id"))
        .replace("{FORMAT}", str(video_dimensions[1]))
        .replace("{RID}", settings.get("rid"))
    )

    try:
        probe = ffmpeg.probe(video)
    except ffmpeg.Error as e:
        raise Exception(e.stderr)

    video_stream = next(
        (stream for stream in probe["streams"] if stream["codec_type"] == "video"), None
    )
    if video_stream is None:
        raise Exception("No video stream found")

    width = int(video_stream["width"])
    height = int(video_stream["height"])
    fps = int(video_stream["nb_frames"])

    is_portrait = height > width
    if is_portrait:
        output_width = video_dimensions[1]
        output_height = video_dimensions[0]
    else:
        output_width = video_dimensions[0]
        output_height = video_dimensions[1]

    # 300p offset
    if height < output_height:
        if (height + 300) < output_height:
            return
        output_height = height
        output_width = width

    font_size = int(math.floor(24 * dimensions.get(str(video_dimensions[1]))[2]))
    video_source = (
        (
            ffmpeg.input(video)
            .filter("scale", output_width, output_height)
            .drawtext(
                fontfile="simhei.ttf",
                text=settings.get("watermark_text"),
                x="w-tw-10",
                y="h-th-10",
                box=1,
                boxcolor="black@0.2",
                fontsize=font_size,
                fontcolor="white",
            )
        )
        if settings.get("use_watermark")
        else (ffmpeg.input(video).filter("scale", output_width, output_height))
    )

    audio_source = ffmpeg.input(audio)
    ffmpeg.output(
        video_source,
        audio_source,
        os.path.join(final_path, final_filename),
        vcodec="libx264",
        acodec="aac",
        crf=video_config.get("crf"),
    ).overwrite_output().run()

    return os.path.join(
        app.config["BASE_DIR"],
        video_path,
        final_filename,
    )


def get_video_screenshot(video, frame_number):
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    _, frame = video.read()
    _, img = cv2.imencode(".png", frame)
    return np.array(img).tobytes()


def create_temporay_audio_file(video):
    video_config = app.config["VIDEO_SETTINGS"]
    final_path = os.path.join(
        app.root_path,
        app.config["BASE_DIR"],
        "tmp",
    )
    print(final_path)
    helper.create_path(final_path)
    filename = f"{helper.get_uuid()}.mp3"
    print(filename)
    video_clip = mp.VideoFileClip(video)
    audio_clip = video_clip.audio
    audio_clip.write_audiofile(
        os.path.join(final_path, filename),
        bitrate=video_config.get("audio_bitrate"),
        fps=video_config.get("audio_sampling_rate"),
    )
    audio_clip.close()
    video_clip.close()
    return os.path.join(final_path, filename)


def create_thumbnail(screenshot, settings, seq: int):
    thumbnail_config = app.config["IMAGE_SETTINGS"]["THUMBNAIL"]
    thumbnail_path = (
        thumbnail_config.get("path")
        .replace("{ID}", settings.get("id"))
        .replace("{SEQ}", str(seq))
        .replace("{RID}", settings.get("rid"))
    )

    final_path = os.path.join(
        app.root_path,
        app.config["BASE_DIR"],
        thumbnail_path,
    )
    helper.create_path(final_path)

    final_filename = "%s%s" % (
        thumbnail_config.get("filename"),
        extensions.get(thumbnail_config.get("extension")),
    )

    final_filename = (
        final_filename.replace("{FILENAME}", settings.get("filename"))
        .replace("{RID}", settings.get("rid"))
        .replace("{SEQ}", str(seq))
    )

    image = Image.open(io.BytesIO(screenshot))
    is_portrait = image.height > image.width
    image.thumbnail((thumbnail_config.get("width"), thumbnail_config.get("height")))
    if thumbnail_config.get("extension") != "PNG":
        image.convert("RGB")

    if is_portrait:
        size = (thumbnail_config.get("width"), thumbnail_config.get("height"))
        background = Image.new("RGB", size, (1, 1, 1))
        background.paste(
            image,
            (int((size[0] - image.size[0]) / 2), int((size[1] - image.size[1]) / 2)),
        )
        if thumbnail_config.get("extension") != "PNG":
            background.convert("RGB")
        background.save(
            os.path.join(final_path, final_filename), thumbnail_config.get("extension")
        )
        background.close()
    else:
        image.save(
            os.path.join(final_path, final_filename), thumbnail_config.get("extension")
        )
    image.close()
    return os.path.join(
        app.config["BASE_DIR"],
        thumbnail_path,
        final_filename,
    )


def create_cover(screenshot, settings):
    cover_config = app.config["IMAGE_SETTINGS"]["COVER"]
    cover_path = (
        cover_config.get("path")
        .replace("{ID}", settings.get("id"))
        .replace("{RID}", settings.get("rid"))
    )
    final_path = os.path.join(
        app.root_path,
        app.config["BASE_DIR"],
        cover_path,
    )
    final_filename = "%s%s" % (
        cover_config.get("filename"),
        extensions.get(cover_config.get("extension")),
    )
    final_filename = final_filename.replace(
        "{FILENAME}", settings.get("filename")
    ).replace("{RID}", settings.get("rid"))
    helper.create_path(final_path)
    image = Image.open(io.BytesIO(screenshot))
    is_portrait = image.height > image.width
    image.thumbnail((cover_config.get("width"), cover_config.get("height")))
    if cover_config.get("extension") != "PNG":
        image.convert("RGB")
    if is_portrait:
        size = (cover_config.get("width"), cover_config.get("height"))
        background = Image.new("RGB", size, (1, 1, 1))
        background.paste(
            image,
            (int((size[0] - image.size[0]) / 2), int((size[1] - image.size[1]) / 2)),
        )
        if cover_config.get("extension") != "PNG":
            background.convert("RGB")
        background.save(
            os.path.join(final_path, final_filename), cover_config.get("extension")
        )
        background.close()
    else:
        image.save(
            os.path.join(final_path, final_filename), cover_config.get("extension")
        )
    image.close()
    return os.path.join(app.config["BASE_DIR"], cover_path, final_filename)
