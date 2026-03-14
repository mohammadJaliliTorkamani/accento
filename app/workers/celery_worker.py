from celery import Celery

from app.core.config import settings
from app.tasks.video_processing import process_video

celery = Celery(
    "accento",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)


@celery.task(bind=True, autoretry_for=(Exception,), retry_backoff=True)
def process_video_task(self, url: str):

    return process_video(url)