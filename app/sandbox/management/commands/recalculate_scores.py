"""
Recalculate scores for existing MessageThread records using ScoringCalculator.
Usage: python manage.py recalculate_scores
"""
from django.core.management.base import BaseCommand

from sandbox.models import MessageThread
from sandbox.scoring_algorithm.scoring import ScoringCalculator


class Command(BaseCommand):
    help = 'Recalculate scores for existing MessageThread records using a ScoringCalculator'

    def handle(self, *args, **options):
        message_threads = MessageThread.objects.all()

        for message_thread in message_threads:
            calculator = ScoringCalculator(
                candidate=message_thread.candidate,
                job=message_thread.job
            )
            score = calculator.calculate_score()
            message_thread.score = score
            message_thread.save()

        self.stdout.write(self.style.SUCCESS('Scores recalculated for all MessageThreads'))
