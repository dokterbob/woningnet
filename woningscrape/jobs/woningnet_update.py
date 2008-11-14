from django_extensions.management.jobs import BaseJob

from woningscrape.get_all import get_woningen

class Job(BaseJob):
    help = "My sample job."

    def execute(self):
        get_woningen()
