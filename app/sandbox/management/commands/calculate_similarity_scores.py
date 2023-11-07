from django.core.management.base import BaseCommand
from sandbox.models import MessageThread
from sandbox.usecases import find_similarities, COEFFICIENTS_VERSION_1


class Command(BaseCommand):
    help = 'Calculate similarity scores for all message threads'

    def handle(self, *args, **options):
        threads = MessageThread.objects.all().select_related(
            'candidate', 'job'
        )

        for thread in threads:
            candidate = thread.candidate
            job = thread.job

            if not job or not candidate:
                continue

            score = find_similarities(candidate, job, COEFFICIENTS_VERSION_1)

            thread.candidate_matching = score

            self.stdout.write(
                self.style.SUCCESS(
                    f'Calculated similarity score '
                    f'for thread {thread.pk}: {score}'
                )
            )

        MessageThread.objects.bulk_update(threads, ["candidate_matching"])
