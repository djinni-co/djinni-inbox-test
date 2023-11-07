from sandbox.models import MessageThread
from sandbox.services.threads_scoring import ThreadScoringService


class ThreadsService:

    @classmethod
    def update_message_thread_scoring(cls, message_thread: MessageThread, save: bool = True) -> MessageThread:
        calculating_service = ThreadScoringService(candidate=message_thread.candidate, job=message_thread.job)
        score = calculating_service.calculate_candidate_score()
        message_thread.score = score.total_score
        message_thread.score_description = score.score_description
        if save:
            message_thread.save(update_fields=['score', 'score_description'])
        return message_thread
