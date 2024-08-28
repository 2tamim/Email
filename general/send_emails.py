from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management.base import BaseCommand
from general.emails import send_email

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        scheduler = BackgroundScheduler()
        scheduler.add_job(send_email, 'date', run_date='2024-12-31 08:00:00')
        scheduler.start()