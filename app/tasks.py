from app import celery
from app import video
from app import image


@celery.task(name="video_task", bind=True)
def video_task(self, file, settings):
    self.update_state(state="STARTED")
    cover, thumbnails, videos = video.process_video(file, settings)
    return {
        "cover": cover,
        "thumbnails": thumbnails,
        "videos": videos,
        "file_type": "video",
        "error": None,
    }


@celery.task(name="image_task", bind=True)
def image_task(self, file, settings):
    self.update_state(state="STARTED")
    img, thumbnail = image.process_image(file, settings)
    return {
        "image": img,
        "thumbnail": thumbnail,
        "file_type": "image",
        "error": None,
    }
