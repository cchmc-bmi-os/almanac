from django.core.management.base import BaseCommand
import sys
import csv
from search.models import Question, Definition, QuestionDefinition


class Command(BaseCommand):
    help = 'Imports a file with cdes and definitions'

    def add_arguments(self, parser):
        parser.add_argument('definition_file', nargs=1, type=str)

    def handle(self, *args, **options):
        definition_data = self.loadFromCsv(options['definition_file'][0])

        for cde in definition_data:
            self.addDefinitionToCde(cde)

    def loadFromCsv(self, input_file):
        sys.stdout.write('Parsing and converting file...')
        data = []

        with open(input_file, 'r', encoding='utf-8', errors='replace') as definition_file:
            dd_reader = csv.reader(definition_file)

            skip_header = True
            for row in dd_reader:
                # skip the first row (header)
                if skip_header is True:
                    skip_header = False
                    continue

                row_data = {
                    'cde': row[0],
                    'definition': row[1]
                }

                # add to results
                data.append(row_data)

        print('Done.')
        return data

    def addDefinitionToCde(self, cde):
        root = Question.objects.filter(name=cde.get('cde')).first()
        if not root:
            # ignore CDE since it doesn't exist
            print('CDE DOES NOT EXIST: {}'.format(cde.get('cde')))
            return

        print('CDE {}'.format(cde.get('cde')))

        # fetch or create a definition
        definition = Definition.objects.filter(
            definition=cde.get('definition')).first()
        if not definition:
            definition = Definition.objects.create(
                definition=cde.get('definition'))
            definition.save()

        # check for current definition
        question_definition = QuestionDefinition.objects.filter(
            question=root, definition=definition).first()
        if not question_definition:
            # fetch all definitions
            question_definitions = QuestionDefinition.objects.filter(
                question=root).order_by('-version')
            next_version = 1
            if question_definitions.count():
                next_version = question_definitions.first().version + 1

            # create the new question definition
            question_definition = QuestionDefinition.objects.create(
                question=root,
                definition=definition,
                version=next_version
            )
            print('Definition created for: {}'.format(cde.get('cde')))
