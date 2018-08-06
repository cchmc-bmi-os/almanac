from django.core.management.base import BaseCommand
from search.models import Question, Condition
import csv


class Command(BaseCommand):
    help = 'Exports the cde and condition data'

    def handle(self, *args, **options):
        headers = ['SITE', 'CDE', 'TEXT']
        conditions_lookup = {}

        # build the condition headers
        idx = 2
        for condition in Condition.objects.order_by('name'):
            headers.append(condition.name)
            conditions_lookup[condition.name] = idx
            idx += 1

        # get the total length of the headers
        total_length = len(headers)

        with open('cde_conditions.csv', 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)

            # write the headers
            csvwriter.writerow(headers)

            # for each question
            for question in Question.objects.order_by('name'):
                site_question = question.site_questions.first()

                # initialize the list
                tmp = [site_question.site.name, site_question.name,
                       site_question.text] + [None] * (total_length - 2)

                # for each condition mark it with an X
                for condition in question.conditions.values_list('name'):
                    tmp[conditions_lookup[condition[0]]] = 'X'

                # write the row
                csvwriter.writerow(tmp)
