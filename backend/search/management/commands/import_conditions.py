from django.core.management.base import BaseCommand
import sys
import csv
from search.models import Question, Condition


class Command(BaseCommand):
    help = 'Imports a DD into the DA'

    keys = [
        'cde',
        'Niemann Pick disease A/B (ASM)',
        'Fabry disease (GLA)',
        'Gaucher disease (GBA)',
        'Pompe disease (GAA)',
        'Krabbe disease (GALC)',
        'Mucopolysaccharidosis (MPS I)'
    ]

    def add_arguments(self, parser):
        parser.add_argument('condition_file', nargs=1, type=str)

    def handle(self, *args, **options):
        condition_data = self.loadFromCsv(options['condition_file'][0])

        for cde in condition_data:
            self.addConditionToCde(cde)

    def loadFromCsv(self, input_file):
        sys.stdout.write('Parsing and converting file...')
        data = []

        with open(input_file, 'r', encoding='utf-8', errors='replace') as condition_file:
            dd_reader = csv.reader(condition_file)

            skip_header = True
            for row in dd_reader:
                # skip the first row (header)
                if skip_header is True:
                    skip_header = False
                    continue

                conditions = []
                for idx in range(1, 7):
                    if row[idx] == 'x':
                        conditions.append(self.keys[idx])

                row_data = {
                    'cde': row[0],
                    'conditions': ','.join(conditions)
                }

                # add to results
                data.append(row_data)

        print('Done.')
        return data

    def addConditionToCde(self, cde):
        root = Question.objects.filter(name=cde.get('cde')).first()
        if not root:
            # ignore CDE since it doesn't exist
            print('CDE DOES NOT EXIST: {}'.format(cde.get('cde')))
            return

        print('CDE {}'.format(cde.get('cde')))
        for condition in cde.get('conditions').split(','):
            if condition:
                try:
                    print ('    Adding condition {}'.format(condition))
                    condition_obj = Condition.objects.get(name=condition)
                    root.conditions.add(condition_obj)
                except:
                    print(condition)
                    # create the new condition
                    print('CONDITION NOT FOUND: {}'.format(condition))
