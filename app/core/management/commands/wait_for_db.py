"""
Django command to wait for database
"""
import time

from django.core.management.base import BaseCommand
from psycopg2 import OperationalError as psycopg2Error

from django.db.utils import OperationalError


class Command(BaseCommand):
    """Django Test"""

    def handle(self, *args, **options):
        """Test function"""
        self.stdout.write("Waiting for database ....")
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (psycopg2Error, OperationalError):
                self.stdout.write("database is unavailable, waiting ...")
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS("Database available !"))
