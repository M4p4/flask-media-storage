class Config(object):
    # BASIC SETTINGS
    BASE_DIR = "media"

    # IMAGE SETTINGS
    # Supported file extension:
    # JPG, WEBP, PNG
    IMAGE_SETTINGS = {
        "THUMBNAIL": {
            "path": "images/{ID}/thumbnails/",
            "filename": "{FILENAME}_{SEQ}",
            "extension": "JPG",
            "width": 240,
            "height": 160,
            "amount": 10,
        },
        "COVER": {
            "path": "images/{ID}/cover/",
            "filename": "{FILENAME}",
            "extension": "JPG",
            "width": 600,
            "height": 400,
        },
    }

    VIDEO_DIR = "videos"
