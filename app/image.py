from app import app


def process_image(source, settings):
    image_settings = app.config["IMAGE_SETTINGS"].get("IMAGE")
