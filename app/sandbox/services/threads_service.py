from django.db.models.signals import post_save

from sandbox.models import MessageThread
from sandbox.services.threads_scoring import ThreadScoringService
from sandbox.signals import update_message_thread_score


class ThreadsService:

    @classmethod
    def update_message_thread_scoring(cls, message_thread: MessageThread, save: bool = True) -> MessageThread:
        post_save.disconnect(update_message_thread_score, sender=MessageThread)
        try:
            calculating_service = ThreadScoringService(candidate=message_thread.candidate, job=message_thread.job)
            score = calculating_service.calculate_candidate_score()
            message_thread.score = score.total_score
            message_thread.score_description = score.score_description
            if save:
                message_thread.save(update_fields=['score', 'score_description'])
            return message_thread
        finally:
            post_save.connect(update_message_thread_score, sender=MessageThread)

