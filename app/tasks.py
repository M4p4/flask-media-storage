from app import celery
from app import video


@celery.task(name="video_task", bind=True)
def video_task(self, filename):
    self.update_state(state="STARTED")
    video_id = 1337
    filename = "test"
    settings = {
        "id": str(video_id),
        "filename": filename,
        "use_watermark": True,
        "watermark_text": "watermark.com",
    }
    cover, thumbnails, videos = video.process_video("", settings)
    return {
        "cover": cover,
        "thumbnails": thumbnails,
        "videos": videos,
        "error": None,
    }
