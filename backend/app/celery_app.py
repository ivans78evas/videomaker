from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    broker_connection_retry_on_startup=True
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,

    # --- Optimization for Free Tier Redis (Upstash) ---
    # Disable internal chatter between workers (reduces command count)
    worker_gossip=False,
    worker_mingle=False,

    # Disable task events (Flower will be less detailed, but saves thousands of commands)
    worker_send_task_events=False,
    task_send_sent_event=False,

    # Reduce polling frequency (Default is often too aggressive for free tiers)
    broker_transport_options={
        'visibility_timeout': 3600,
        'polling_interval': 10  # Check for new tasks every 10s instead of 1s
    },

    # Results cleanup (Saves storage)
    result_expires=3600,  # Clear results after 1 hour

    # Disable remote control (Saves commands used for inspect/control)
    # Note: This will disable the /workers API endpoint, but it's necessary to save quota.
    worker_enable_remote_control=False,

    # --- Priority & Routing Configuration ---
    task_default_queue='default',
    task_queues={
        'urgent_tasks': {
            'exchange': 'urgent_tasks',
            'routing_key': 'urgent_tasks',
        },
        'default': {
            'exchange': 'default',
            'routing_key': 'default',
        },
        'bulk_tasks': {
            'exchange': 'bulk_tasks',
            'routing_key': 'bulk_tasks',
        },
    },
    task_routes={
        'tasks.process_translation_urgent': {'queue': 'urgent_tasks'},
        'tasks.process_translation_bulk': {'queue': 'bulk_tasks'},
    },
)

# Use include to avoid circular imports
celery_app.conf.update(
    include=['app.tasks.translation']
)
