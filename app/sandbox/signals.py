from django.db.models.signals import post_save
from django.dispatch import receiver

from sandbox.models import MessageThread
from sandbox.tasks import update_message_thread_scoring_task


@receiver(post_save, sender=MessageThread)
def update_message_thread_score(sender, instance, created, **kwargs):
    if getattr(instance, 'skip_signal', False):
        return
    update_message_thread_scoring_task.s(instance.id).apply_async()
