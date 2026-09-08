import time

_command_import_started = time.perf_counter()
print("BOOT run_poll_and_process import entered", flush=True)

from django.core.management.base import BaseCommand

print(
    f"BOOT BaseCommand import complete elapsed={time.perf_counter() - _command_import_started:.3f}s",
    flush=True,
)

from jobs.runner import poll_and_process

print(
    f"BOOT jobs.runner import complete elapsed={time.perf_counter() - _command_import_started:.3f}s",
    flush=True,
)

class Command(BaseCommand):
    help = "Claim and process one pending job."

    def handle(self, *args, **options):
        print("BOOT command handle entered", flush=True)
        poll_and_process()
