from django.core.management.base import BaseCommand

from jobs.runner import poll_and_process

class Command(BaseCommand):
    help = "Claim and process one pending job."

    def handle(self, *args, **options):
        poll_and_process()
