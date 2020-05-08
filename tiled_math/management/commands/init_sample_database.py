from django.core.management.base import BaseCommand

from tags.tests import add_tags_to_problems_randomly, add_sample_tags
from folder.tests import add_sample_folders
from problems.tests import add_sample_problems, add_problems_to_folders_randomly

class Command(BaseCommand):
    help = 'Adds sample tags/folders/problems'

    def handle(self, *args, **kwargs):
        self.stdout.write("Adding sample problems")
        add_sample_problems()

        self.stdout.write("Adding sample tags")
        add_sample_tags()

        self.stdout.write("Adding tags to problems randomly")
        add_tags_to_problems_randomly()

        self.stdout.write("Adding sample folders")
        add_sample_folders()

        self.stdout.write("Adding problems to folders randomly")
        add_problems_to_folders_randomly()

        self.stdout.write(self.style.SUCCESS("Done."))
