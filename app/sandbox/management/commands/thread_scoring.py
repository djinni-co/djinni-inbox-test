from itertools import islice
from concurrent import futures

from django.core.management.base import BaseCommand
from sandbox.models import MessageThread
from sandbox.scoring_mechanism import BulkThreadScore


class Command(BaseCommand):

    def handle(self, *args, **options):
        with futures.ThreadPoolExecutor() as executor:
            executor.map(BulkThreadScore().bulk_score, self.get_threads_in_chunks())

    @staticmethod
    def get_threads_in_chunks(chunk_size=500):
        threads = MessageThread.objects.all().iterator(chunk_size=chunk_size)
        while True:
            chunk = list(islice(threads, chunk_size))
            if not chunk:
                break
            yield chunk

