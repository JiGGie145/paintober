#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import time

_boot_started = time.perf_counter()
print(f"BOOT manage.py entered pid={os.getpid()} elapsed=0.000s", flush=True)


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paintober_backend.settings')
    try:
        from django.core.management import execute_from_command_line
        print(
            f"BOOT Django management import complete elapsed={time.perf_counter() - _boot_started:.3f}s",
            flush=True,
        )
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
