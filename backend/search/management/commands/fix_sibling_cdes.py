from django.core.management.base import BaseCommand
from search.models import Question


class Command(BaseCommand):
    help = 'Fixes the sib9 and sib10 cde conditions'

    def handle(self, *args, **options):
        # get the sib_8 cde conditions
        sib8 = Question.objects.filter(name__icontains='sib_8').first()

        # don't do anything if it is not found
        if not sib8:
            return

        all_conditions = sib8.conditions.all()

        for sib_type in ['sib_9', 'sib_10']:
            for question in Question.objects.filter(name__icontains=sib_type):
                question.conditions.add(*all_conditions)
