from django.core.management import base

from kbde.django.storages import cleaner

import time


class Command(base.BaseCommand):
    
    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help=(
                "Don't delete anything. Print a message for each object "
                "instead."
            ),
        )
        parser.add_argument(
            "--loop-interval",
            type=int,
            default=0,
            help=(
                "Run this command in a loop for ever, with an interval of "
                "this many minutes."
            ),
        )

    def handle(self, **options):
        cleaner_instance = cleaner.S3Cleaner(stdout=self.stdout)

        kwargs = {
            "dry_run": options["dry_run"],
        }

        if not options["loop_interval"]:
            cleaner_instance.clean(**kwargs)

        else:
            while True:
                cleaner_instance.clean(**kwargs)
                time.sleep(options["loop_interval"] * 60)
