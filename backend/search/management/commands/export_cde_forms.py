from django.core.management.base import BaseCommand
from search.models import SiteQuestion
import csv


class Command(BaseCommand):
    help = 'Exports the cde and its form > section'

    def handle(self, *args, **options):
        headers = ['PROJECT', 'ROOT', 'CDE', 'FORM', 'SECTION', 'TYPE', 'TEXT', 'CHOICES', 'IS_DEFAULT', 'PROJECT_ORDER', 'ID', 'PROJECT_ID', 'ROOT_ID']

        with open('cde_forms.csv', 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)

            # write the headers
            csvwriter.writerow(headers)

            # for each question
            for site_question in SiteQuestion.objects.prefetch_related('question').prefetch_related('site').prefetch_related('form').prefetch_related('tags').order_by('name'):
                choices = ['{}, {}'.format(choice.value, choice.text) for choice in site_question.choices.all()]
                is_default = site_question.tags.filter(label__label='LpdrDefault', value=True).first()

                tmp = [
                    site_question.site.name,
                    site_question.question.name,
                    site_question.name,
                    site_question.form.name,
                    site_question.form.section,
                    site_question.type,
                    site_question.text,
                    site_question.calculation if site_question.type == 'calc' else ' | '.join(choices),
                    'Y' if is_default else 'N',
                    site_question.ordering,
                    site_question.id,
                    site_question.site.id,
                    site_question.question.id
                ]

                # write the row
                csvwriter.writerow(tmp)
