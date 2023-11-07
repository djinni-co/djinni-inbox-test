from django.core.management.base import BaseCommand, CommandError

from sandbox.models import MessageThread
from sandbox.services.threads_service import ThreadsService


class Command(BaseCommand):
    help = "Recalculates the score for every thread in the database."

    def handle(self, *args, **options):
        for instance in MessageThread.objects.all().iterator():
            try:
                ThreadsService.update_message_thread_scoring(message_thread=instance)
            except Exception as e:
                raise CommandError(f'Error updating thread {instance.id}: {e}')

        count_threads = MessageThread.objects.count()
        self.stdout.write(
            self.style.SUCCESS(f'Successfully recalculated score for {count_threads} threads.')
        )
