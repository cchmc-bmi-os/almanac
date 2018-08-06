from django.core.management.base import BaseCommand
import sys
import csv
from search.models import Question, Definition, QuestionDefinition, Source
from django.db import connections


class Command(BaseCommand):
    help = 'Imports a definition data from LPDR CHOP'

    def dictfetchall(self):
        "Return all rows from a cursor as a dict"
        columns = [col[0] for col in self.cursor.description]
        return [
            dict(zip(columns, row))
            for row in self.cursor.fetchall()
        ]

    def handle(self, *args, **options):
        # save the updated information
        connections.databases['old'] = {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'HOST': 'localhost',
            'PORT': '5432',
            'NAME': 'almanac_lpdr',
            'USER': 'root',
            'PASSWORD': 'secret'
        }

        # connect to the old database
        self.cursor = connections['old'].cursor()

        self.cursor.execute("SELECT dictionary_question.field_name AS cde, dictionary_question.definition, dictionary_question.definition_note, dictionary_source.name AS definition_source, dictionary_source.address AS definition_source_address, dictionary_sitequestion.question_id FROM dictionary_sitequestion LEFT JOIN dictionary_site ON dictionary_site.id = dictionary_sitequestion.site_id LEFT JOIN dictionary_siteform ON dictionary_siteform.id = dictionary_sitequestion.site_form_id LEFT JOIN dictionary_question ON dictionary_question.id = dictionary_sitequestion.question_id LEFT JOIN dictionary_form ON dictionary_form.id = dictionary_siteform.form_id LEFT JOIN dictionary_source ON dictionary_source.id = dictionary_question.definition_source_id WHERE dictionary_sitequestion.current = True AND dictionary_site.live = True ORDER BY dictionary_siteform.order, dictionary_siteform.section_order")
        definition_data = self.dictfetchall()

        for cde in definition_data:
            if cde.get('definition'):
                self.addDefinitionToCde(cde)

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
            definition = Definition.objects.create(definition=cde.get('definition'))
            definition.save()

        # check for current definition
        question_definition = QuestionDefinition.objects.filter(question=root, definition=definition).first()

        if not question_definition:
            # fetch all definitions
            question_definitions = QuestionDefinition.objects.filter(question=root).order_by('-version')
            next_version = 1
            if question_definitions.count():
                next_version = question_definitions.first().version + 1

            # create the new question definition
            question_definition = QuestionDefinition.objects.create(
                question=root,
                definition=definition,
                version=next_version
            )
            print('  Creating a definition.')

        if cde.get('definition_note'):
            print('  Adding a definition note.')
            definition.note = cde.get('definition_note')
            definition.save()

        if cde.get('definition_source'):
            print('  Adding a definition source.')
            source = Source.objects.get_or_create(name=cde.get('definition_source'), address=cde.get('definition_source_address'))
            definition.source = source[0]
            definition.save()
