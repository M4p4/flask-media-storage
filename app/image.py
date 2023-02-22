from app import app
from PIL import Image, ImageOps, ExifTags, ImageDraw, ImageFont
from app import helper
import os

extensions = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}


def process_image(source, settings):
    try:
        image_settings = app.config["IMAGE_SETTINGS"].get("IMAGE")
        image_path = (
            image_settings.get("path")
            .replace("{ID}", settings.get("id"))
            .replace("{RID}", settings.get("rid"))
        )
        final_path = os.path.join(
            app.root_path,
            app.config["BASE_DIR"],
            image_path,
        )
        final_filename = "%s%s" % (
            image_settings.get("filename"),
            extensions[image_settings.get("extension")],
        )
        final_filename = final_filename.replace(
            "{FILENAME}", settings.get("filename")
        ).replace("{RID}", settings.get("rid"))

        images = [
            {
                "path": final_path,
                "width": image_settings.get("width"),
                "thumbnail": False,
            },
            {
                "path": os.path.join(final_path, image_settings.get("thumbnail_path")),
                "width": image_settings.get("thumbnail_width"),
                "thumbnail": True,
            },
        ]

        for current_image in images:
            if not image_settings.get("generate_thumbnail") and current_image.get(
                "thumbnail"
            ):
                break
            helper.create_path(current_image.get("path"))
            img = Image.open(source)

            # fix rotation problems source: https://stackoverflow.com/questions/4228530/pil-thumbnail-is-rotating-my-image
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == "Orientation":
                    break
            exif = dict(img._getexif().items())

            if exif[orientation] == 3:
                img = img.rotate(180, expand=True)
            elif exif[orientation] == 6:
                img = img.rotate(270, expand=True)
            elif exif[orientation] == 8:
                img = img.rotate(90, expand=True)

            if current_image.get("thumbnail"):
                thumb = ImageOps.fit(
                    img, (current_image.get("width"), current_image.get("width"))
                )
                thumb.save(os.path.join(current_image.get("path"), final_filename))
            else:
                is_portrait = img.height > img.width
                output_height = img.height
                output_width = img.width
                if is_portrait and img.width > current_image.get("width"):
                    output_height = current_image.get("width")
                    output_width = int(
                        img.width * current_image.get("width") / img.height
                    )
                elif img.width > current_image.get("width"):
                    output_width = current_image.get("width")
                    output_height = int(
                        img.height * current_image.get("width") / img.width
                    )
                resized_img = img.resize((output_width, output_height))

                # watermark
                if settings.get("use_watermark"):
                    draw = ImageDraw.Draw(resized_img)
                    text = settings.get("watermark_text")
                    font = ImageFont.truetype(
                        os.path.join(app.root_path, "fonts/arial.ttf"), 30
                    )
                    text_w, text_h = draw.textsize(text, font=font)
                    watermark = Image.new(
                        "RGBA", (text_w + 20, text_h + 10), (1, 1, 1, 87)
                    )
                    draw = ImageDraw.Draw(watermark)

                    draw.text(
                        (10, 1),
                        text,
                        font=font,
                        fill=(255, 255, 255),
                    )
                    resized_img.paste(
                        watermark,
                        (
                            resized_img.size[0] - watermark.size[0] - 10,
                            resized_img.size[1] - watermark.size[1] - 10,
                        ),
                        watermark,
                    )

                resized_img.save(
                    os.path.join(current_image.get("path"), final_filename)
                )
            img.close()
        helper.delete_file(source)
    except Exception as e:
        print(str(e))
        # rollback
        helper.delete_file(source)
        helper.delete_file(os.path.join(app.root_path, final_path, final_filename))
        helper.delete_file(
            os.path.join(
                final_path, image_settings.get("thumbnail_path"), final_filename
            )
        )
        return None, None

    return (
        os.path.join(app.config["BASE_DIR"], image_path, final_filename),
        os.path.join(
            app.config["BASE_DIR"],
            image_path,
            image_settings.get("thumbnail_path"),
            final_filename,
        )
        if image_settings.get("generate_thumbnail")
        else None,
    )
