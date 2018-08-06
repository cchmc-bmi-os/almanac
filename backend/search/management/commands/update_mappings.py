from django.core.management.base import BaseCommand
import sys
from search.models import Condition, ConditionCategory, Site, Question, SiteQuestion, Form
import os
import json
import csv


class Command(BaseCommand):
    help = 'Updates the mapping based on csv'
    site_mapping = {
        'ArkansasMSMS': 'Arkansas MS/MS',
        'ArkansasHemoglobinopathies': 'Arkansas Hemoglobinopathies',
        'ArkansasHearingScreened': 'Arkansas Hearing Screen',
        'ArkansasGALT': 'Arkansas GALT',
        'ArkansasCH': 'Arkansas CH',
        'ArkansasCF': 'Arkansas CF',
        'ArkansasCDE': 'Arkansas CDE',
        'ArkansasCAH': 'Arkansas CAH',
        'ArkansasBIOT': 'Arkansas BIOT',
        'NBSTRNCore': 'NBSTRN Core',
        'PublicHealth': 'Public Health',
    }

    def add_arguments(self, parser):
        parser.add_argument('mapping_file', nargs=1, type=str)

    def handle(self, *args, **options):
        if not os.path.isfile(options['mapping_file'][0]):
            print('Mapping file is not found')
            print('')
            sys.exit()

        data = self.update_mappings(options['mapping_file'][0])

    def update_mappings(self, input_file):
        site_lookup = {item.name: item for item in Site.objects.all()}

        with open(input_file, 'r', encoding='utf-8', errors='replace') as mapping_file:
            mappings = csv.reader(mapping_file)

            skip_header = True
            for row in mappings:
                # skip the first row (header)
                if skip_header is True:
                    skip_header = False
                    continue

                # row_data = {
                #     'map_to': row[0],
                #     'name': row[1],
                #     'project':
                #     'is_defualt': row[21]
                # }

                # take off the __ stuff
                root_name = row[0]
                if '__' in row[0]:
                    root_name = row[0].split('__')[0]

                # find the site
                site = site_lookup[self.normalize_site(row[18])]

                # find the root question
                root_question = Question.objects.get(name=root_name)

                # find the form
                # print(row[20], row[3])
                # form = Form.objects.get(name=row[2], section=row[3])

                # find the site_question form the site

                found = False
                for site_question in root_question.site_questions.filter(name__icontains=root_name, site=site):
                    if row[19] and int(row[19]) == int(site_question.ordering):
                        print('FOUND {} ({}, {}):'.format(root_question.name, root_question.id, site.name))
                        found = True

                if not found:
                    print('NOT FOUND {} ({}, {}):'.format(root_question.name, root_question.id, site.name))


                # site_question = SiteQuestion.objects.get(name__icontains=row[0], site=site)

                # if site_question.question.id != root_question.id:
                #     print('Not Mapped')
                #     print('  ROOT: {}'.format(row[0]))
                #     print('  SITE: {}'.forat(row[18]))
                #     print('  SITE Q ROOT: {}'.format(site_question.question.name))

    def normalize_site(self, site_name):
        if site_name in self.site_mapping:
            return self.site_mapping[site_name]

        return site_name
