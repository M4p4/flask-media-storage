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
    }

    # VIDEO SETTINGS
    # Supported quality formats
    # 720, 480, 360
    VIDEO_SETTINGS = {
        "formats": [360],
        "path": "videos/{ID}/",
        "filename": "{FILENAME}_{FORMAT}",
    }

    VIDEO_DIR = "videos"
