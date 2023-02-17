class Config(object):
    # BASIC SETTINGS
    BASE_DIR = "media"

    # IMAGE SETTINGS
    # Supported file extension:
    # JPEG, WEBP, PNG
    IMAGE_SETTINGS = {
        "THUMBNAIL": {
            "path": "images/{ID}/thumbnails/",
            "filename": "{FILENAME}_{SEQ}",
            "extension": "JPEG",
            "width": 360,
            "height": 240,
            "amount": 10,
        },
        "COVER": {
            "path": "images/{ID}/cover/",
            "filename": "{FILENAME}",
            "extension": "JPEG",
            "width": 600,
            "height": 400,
        },
        "IMAGE": {
            "path": "images/{RANDOM}/",
            "filename": "{FILENAME}",
            "extension": "JPEG",
        },
    }

    # VIDEO SETTINGS
    # Supported quality formats
    # 1080, 720, 480, 360
    VIDEO_SETTINGS = {
        "formats": [360, 480, 720, 1080],
        "path": "videos/{ID}/",
        "filename": "{FILENAME}_{FORMAT}",
        "audio_bitrate": "64k",
        "audio_sampling_rate": 22050,
    }
