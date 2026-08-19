from unittest.mock import patch

from django.core.management import call_command
from django.test import SimpleTestCase


class RunPollAndProcessCommandTests(SimpleTestCase):
    @patch("jobs.management.commands.run_poll_and_process.poll_and_process")
    def test_command_processes_one_job(self, process_job):
        call_command("run_poll_and_process")

        process_job.assert_called_once_with()