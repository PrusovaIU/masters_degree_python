import os

os.environ.setdefault(
    'CELERY_CUSTOM_WORKER_POOL',
    'celery_aio_pool.pool:AsyncIOPool'
)

from celery import Celery

from chat_api_service.app.core.config import settings

celery_app = Celery(
    "chat_api_service",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["chat_api_service.app.tasks.llm_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],

    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_track_started=True,
    task_reject_on_worker_lost=True,
    worker_max_tasks_per_child=1000,

    task_soft_time_limit=300,
    task_time_limit=360,

    broker_connection_retry_on_startup=True
)

celery_app.autodiscover_tasks(
    packages=["chat_api_service.app.tasks"],
    force=True
)
