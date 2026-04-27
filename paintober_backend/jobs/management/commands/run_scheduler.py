import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django.conf import settings
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore

from jobs.runner import poll_and_process

logger = logging.getLogger("jobs")


class Command(BaseCommand):
    help = "Start the APScheduler job polling loop."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone="UTC")
        scheduler.add_jobstore(DjangoJobStore(), "default")

        interval = getattr(settings, "JOB_POLL_INTERVAL_SECONDS", 5)

        scheduler.add_job(
            poll_and_process,
            trigger=IntervalTrigger(seconds=interval),
            id="poll_and_process",
            name="Poll and process pending jobs",
            jobstore="default",
            replace_existing=True,
            max_instances=1,
            misfire_grace_time=30,
        )

        logger.info("Scheduler starting | poll_interval=%ds", interval)
        self.stdout.write(
            self.style.SUCCESS(f"Scheduler started (poll every {interval}s). Press Ctrl+C to stop.")
        )

        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
            logger.info("Scheduler stopped.")
            self.stdout.write(self.style.WARNING("Scheduler stopped."))
