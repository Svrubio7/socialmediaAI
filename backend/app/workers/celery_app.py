"""
Celery application configuration.
"""

from celery import Celery
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "social_media_ai",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.workers.video_tasks",
        "app.workers.publish_tasks",
    ],
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task execution settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_concurrency=2,
    
    # Result settings
    result_expires=3600,  # 1 hour
    
    # Beat settings for scheduled tasks
    beat_schedule={
        "collect-analytics-hourly": {
            "task": "app.workers.publish_tasks.collect_analytics",
            "schedule": 3600.0,  # Every hour
        },
        "refresh-tokens-daily": {
            "task": "app.workers.publish_tasks.refresh_expiring_tokens",
            "schedule": 86400.0,  # Every day
        },
        "check-scheduled-posts": {
            "task": "app.workers.publish_tasks.process_scheduled_posts",
            "schedule": 60.0,  # Every minute
        },
    },
    
    # Retry settings
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
)

# Task routing
celery_app.conf.task_routes = {
    "app.workers.video_tasks.*": {"queue": "video_processing"},
    "app.workers.publish_tasks.*": {"queue": "publishing"},
}
