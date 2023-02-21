from app import celery
from app import video


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
