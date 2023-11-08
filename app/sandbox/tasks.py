from project import celery_app
from sandbox.models import MessageThread
from sandbox.services.threads_service import ThreadsService


@celery_app.task
def update_message_thread_scoring_task(message_thread_id: int) -> None:
    message_thread = MessageThread.objects.get(id=message_thread_id)
    ThreadsService.update_message_thread_scoring(message_thread=message_thread)
