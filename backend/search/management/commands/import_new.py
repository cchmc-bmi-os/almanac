from search.models import *
from django.core.management.base import BaseCommand
from django.db import connections
from django.core import management
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.contrib.auth.models import User
from getpass import getpass
import sys
import traceback


class Command(BaseCommand):
    help = 'Imports old db data into new schema'
    cursor = None

    def dictfetchall(self):
        "Return all rows from a cursor as a dict"
        columns = [col[0] for col in self.cursor.description]
        return [
            dict(zip(columns, row))
            for row in self.cursor.fetchall()
        ]

    def handle(self, *args, **options):
        self.clearDatabase()
        self.importUsers()
        self.importSources()
        self.importDefinitions()
        self.importChoices()
        self.importQuestions()
        self.importSites()
        self.importForms()
        # self.importConditionCategories()
        self.importSiteQuestions()
        self.importQuestionChoices()
        self.importCodeTypes()
        self.importCodes()
        self.importQuestionCodes()
        # self.importConditions()
        self.importQuestionConditions()
        self.importQuestionDefinitions()
        self.importChoiceDefinitions()
        self.importChoiceCodes()

        # update the conditions again, just in case
        management.call_command('update_conditions')

    def clearDatabase(self):
        management.call_command('setup_data_almanac')

        print('')
        print('Import from Database: POSTGRES')

        # get all the database connection information
        tmp_settings = {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
        }
        for key in ['HOST', 'PORT', 'NAME', 'USER', 'PASSWORD']:
            data = ''
            while data == '':
                if key == 'PASSWORD':
                    data = getpass(prompt='  Database PASSWORD: ')
                else:
                    data = input('  Database {}: '.format(key))

                if data == '':
                    print('Please enter a {}'.format(key.lower()))

            tmp_settings[key] = data

        # save the updated information
        connections.databases['old'] = tmp_settings

        # connect to the old database
        self.cursor = connections['old'].cursor()
        print('')

    def importUsers(self):
        sys.stdout.write('Importing Users...')
        sys.stdout.flush()
        self.cursor.execute("SELECT * FROM public.auth_user")
        for data in self.dictfetchall():
            try:
                username = data.get('username').lower()

                if 'user' not in username:
                    user = User(
                        username=username,
                        first_name=data.get('first_name'),
                        last_name=data.get('last_name'),
                        email=data.get('email').lower(),
                        password=data.get('password'),
                        is_staff=data.get('is_staff'),
                        is_active=data.get('is_active'),
                        is_superuser=data.get('is_superuser'),
                        last_login=data.get('last_login'),
                        date_joined=data.get('date_joined')
                    )
                    user.save()
            except IntegrityError:
                pass

        print('Done.')

    def importSources(self):
        sys.stdout.write('Importing Sources...')
        sys.stdout.flush()
        self.cursor.execute("SELECT name, address FROM dictionary_source")
        for data in self.dictfetchall():
            source = Source(
                name=str(data.get('name')).strip(),
                address=str(data.get('address')).strip()
            )
            source.save()

        print('Done.')

    def importDefinitions(self):
        sys.stdout.write('Importing Definitions...')
        sys.stdout.flush()
        self.cursor.execute("SELECT DISTINCT(definition) definition, definition_note, name, address FROM dictionary_question LEFT JOIN dictionary_source ON dictionary_source.id = dictionary_question.definition_source_id WHERE definition IS NOT NULL AND current = True")
        for data in self.cursor.fetchall():
            try:
                definition = Definition.objects.get(definition=data[0])
            except ObjectDoesNotExist:
                if data[2]:
                    try:
                        source = Source.objects.get(
                            name=str(data[2]).strip(), address=str(data[3]).strip())
                    except MultipleObjectsReturned:
                        print("Multiple Sources: {}".format(data[2]))
                        return
                    except ObjectDoesNotExist:
                        print('Does not exists: \'{}\': \'{}\''.format(
                            data[2], data[3]))
                        return
                else:
                    source = None

                definition = Definition(
                    definition=data[0],
                    note=data[1],
                    source=source
                )
                definition.save()

        self.cursor.execute("SELECT DISTINCT(definition) definition, definition_note, name, address  FROM dictionary_choice LEFT JOIN dictionary_source ON dictionary_source.id = dictionary_choice.definition_source_id WHERE definition IS NOT NULL")
        for data in self.cursor.fetchall():
            try:
                definition = Definition.objects.get(definition=data[0])
            except ObjectDoesNotExist:
                if data[2]:
                    try:
                        source = Source.objects.get(
                            name=str(data[2]).strip(), address=str(data[3]).strip())
                    except MultipleObjectsReturned:
                        print("Multiple Sources: {}".format(data[2]))
                        return
                else:
                    source = None

                definition = Definition(
                    definition=data[0],
                    note=data[1],
                    source=source
                )
                definition.save()
        print('Done.')

    def importChoices(self):
        sys.stdout.write('Importing Choices...')
        sys.stdout.flush()
        self.cursor.execute("SELECT DISTINCT(value) FROM dictionary_choice")
        for data in self.cursor.fetchall():
            choice = Choice(
                text=data[0],
                value=data[0]
            )
            choice.save()

        print('Done.')

    def importQuestions(self):
        sys.stdout.write('Importing Questions...')
        sys.stdout.flush()
        self.cursor.execute(
            "SELECT DISTINCT ON (field_name) field_name FROM dictionary_question WHERE current = True")
        for data in self.cursor.fetchall():
            question = Question(
                name=data[0],
            )
            question.save()

        print('Done.')

    def importSites(self):
        sys.stdout.write('Importing Sites...')
        sys.stdout.flush()
        self.cursor.execute("SELECT * FROM dictionary_site")
        lookup = {
            'IBEMC': 'Inborn Errors of Metabolism',
            'University of Utah': 'Spinal Muscular Atrophy',
            'Mount Sinai': 'Mount Sinai'
        }

        for data in self.cursor.fetchall():
            site = Site(
                name=data[2],
                display='{}'.format(lookup[data[2]]),
                pi=data[3],
                is_live=data[5],
            )
            site.save()

        print('Done.')

    def importForms(self):
        sys.stdout.write('Importing Forms...')
        sys.stdout.flush()
        self.cursor.execute(
            "SELECT DISTINCT ON (name, section) trim(both from name) AS name, trim(both from section) AS section FROM dictionary_form")
        for data in self.cursor.fetchall():

            section = str(data[1]).strip() if data[1] else None

            form = Form(
                name=str(data[0]).strip(),
                section=section,
            )
            form.save()

        print('Done.')

    def importConditionCategories(self):
        sys.stdout.write('Importing ConditionCategories...')
        sys.stdout.flush()
        lookup = {
            'Fatty acid oxidation disorders': 'u_cond_faod',
            'Organic acid disorders': 'u_cond_org_acid',
            'Other disorders': 'u_cond_other',
            'Amino acid disorders': 'u_cond_amino_acid',
            'Endocrine disorders': 'u_cond_endo',
            'Hemoglobin disorders': 'u_cond_hemo',
            'SACHDNC candidate disorders': 'u_cond_cand',
            'Condition not listed': 'u_cond_na',
        }
        self.cursor.execute(
            "SELECT DISTINCT(value), order_number FROM logic_labels_logiclabel WHERE rule_id = 10")
        for data in self.cursor.fetchall():
            category = ConditionCategory(
                label=data[0],
                name=lookup[data[0]],
                ordering=data[1],
            )
            category.save()

        print('Done.')

    def importSiteQuestions(self):
        sys.stdout.write('Importing SiteQuestions...')
        sys.stdout.flush()
        self.cursor.execute("SELECT dictionary_site.name AS site, dictionary_form.name AS form, dictionary_form.section AS section,  dictionary_question.field_name, dictionary_question.field_text, dictionary_question.field_type, dictionary_question.field_note, dictionary_question.min_val, dictionary_question.max_val, dictionary_question.calculation, dictionary_question.order_number, dictionary_question.align, dictionary_question.matrix_name, dictionary_question.unknown, dictionary_sitequestion.branching_logic, dictionary_question.identifier, dictionary_question.required, dictionary_siteform.order AS form_order, dictionary_siteform.section_order FROM dictionary_sitequestion LEFT JOIN dictionary_site ON dictionary_site.id = dictionary_sitequestion.site_id LEFT JOIN dictionary_siteform ON dictionary_siteform.id = dictionary_sitequestion.site_form_id LEFT JOIN dictionary_question ON dictionary_question.id = dictionary_sitequestion.question_id LEFT JOIN dictionary_form ON dictionary_form.id = dictionary_siteform.form_id WHERE dictionary_sitequestion.current = True ORDER BY dictionary_siteform.order, dictionary_siteform.section_order")
        for data in self.cursor.fetchall():
            try:
                site = Site.objects.get(name=data[0])
            except MultipleObjectsReturned:
                print("Multiple Sites: {}".format(data[0]))
                return

            try:
                form = Form.objects.get(name=data[1], section=data[2])
            except MultipleObjectsReturned:
                print("Multiple Forms: {} > {}".format(data[1], data[2]))
                return
            except ObjectDoesNotExist:
                print("No Forms: {} > {}".format(data[1], data[2]))
                return

            try:
                question = Question.objects.get(name=data[3])
            except MultipleObjectsReturned:
                print("Multiple Questions: {}".format(data[3]))
                return

            # tags to add
            tags = [
                {'label': 'Identifier', 'value': data[15]},
                {'label': 'Required', 'value': data[16]}
            ]

            # add the default tag if its the first one
            if question.site_questions.count() < 1:
                tags.append({'label': 'LpdrDefault', 'value': True})

            # if data[16] is True:
            #     print(data)
            #     print(tags)

            site_question = SiteQuestion(
                site=site,
                form=form,
                question=question,
                # is_default=default,
                name=data[3],
                text=data[4],
                type=data[5],
                note=data[6],
                min_val=data[7],
                max_val=data[8],
                calculation=data[9],
                ordering=data[10],
                align=data[11],
                matrix_name=data[12],
                unknown_val=data[13],
                branching_logic=data[14],
                # status=status,
                # is_identifier=data[15],
                # is_required=data[16],
            )
            site_question.save()

            for tag in tags:
                tag_label = TagLabel.objects.get(label=tag.get('label'))

                try:
                    new_tag = Tag.objects.get(
                        value=tag.get('value'), label=tag_label)
                except ObjectDoesNotExist:
                    new_tag = Tag(value=tag.get('value'), label=tag_label)

                new_tag.save()
                site_question.tags.add(new_tag)

        print('Done.')

    def importQuestionChoices(self):
        sys.stdout.write('Importing QuestionChoices...')
        sys.stdout.flush()
        self.cursor.execute("SELECT dictionary_question.field_name, string_agg(dictionary_choice.value, '::'), string_agg(to_char(dictionary_choice.order_number, '9999'), '::') FROM dictionary_choice LEFT JOIN dictionary_question ON dictionary_question.id = dictionary_choice.question_id WHERE dictionary_question.current = True GROUP BY dictionary_question.field_name")
        for data in self.cursor.fetchall():
            choices = data[1].split('::')
            values = data[2].split('::')

            for choice in choices:
                site_questions = SiteQuestion.objects.filter(name=data[0])
                dbChoice = Choice.objects.get(text=choice)

                for site_question in site_questions:
                    question_choice = SiteQuestionChoice(
                        site_question=site_question,
                        choice=dbChoice,
                        ordering=values[choices.index(choice)]
                    )
                    question_choice.save()

        print('Done.')

    def importCodeTypes(self):
        sys.stdout.write('Importing CodeTypes...')
        sys.stdout.flush()
        self.cursor.execute(
            "SELECT dictionary_codetype.name, description, base_url, dictionary_source.name AS source FROM dictionary_codetype LEFT JOIN dictionary_source ON dictionary_source.id = dictionary_codetype.source_id")
        for data in self.cursor.fetchall():
            source = Source.objects.get(name=data[3])

            code_type = CodeType(
                source=source,
                name=data[0],
                description=data[1],
                note=data[2]
            )
            code_type.save()

        print('Done.')

    def importCodes(self):
        sys.stdout.write('Importing Codes...')
        sys.stdout.flush()
        self.cursor.execute(
            "SELECT dictionary_code.value, dictionary_code.note, dictionary_codetype.name FROM dictionary_code LEFT JOIN dictionary_codetype ON dictionary_codetype.id = dictionary_code.code_type_id")
        for data in self.cursor.fetchall():
            code_type = CodeType.objects.get(name=data[2])

            try:
                code = Code.objects.get(value=data[0], code_type=code_type)
            except ObjectDoesNotExist:
                code = Code(
                    code_type=code_type,
                    value=data[0],
                    note=data[1]
                )
                code.save()

        print('Done.')

    def importQuestionCodes(self):
        sys.stdout.write('Importing QuestionCodes...')
        sys.stdout.flush()
        self.cursor.execute("SELECT dictionary_code.value, dictionary_question.field_name FROM dictionary_question_codes LEFT JOIN dictionary_code ON dictionary_code.id = dictionary_question_codes.code_id LEFT JOIN dictionary_question ON dictionary_question.id = dictionary_question_codes.question_id")
        for data in self.cursor.fetchall():
            code = Code.objects.get(value=data[0])
            site_questions = SiteQuestion.objects.filter(name=data[1])

            for site_question in site_questions:
                site_question.question.codes.add(code)

        print('Done.')

    def importConditions(self):
        sys.stdout.write('Importing Conditions...')
        sys.stdout.flush()
        self.cursor.execute(
            "SELECT field_name, value, order_number FROM logic_labels_logiclabel WHERE field_name <> 'u_patient_condition_cat'")
        for data in self.cursor.fetchall():
            try:
                category = ConditionCategory.objects.get(name=data[0])
                condition = Condition(
                    category=category,
                    label=data[1],
                    name=data[1],
                    ordering=data[2]
                )
                condition.save()
            except Exception as e:
                print(data)
                print(e)
                sys.exit()

        print('Done.')

    def importQuestionConditions(self):
        sys.stdout.write('Importing QuestionConditions...')
        sys.stdout.flush()

        condition_lookup = {
            'Fabry': 'Fabry disease (GLA)',
            'Niemann Pick Types A and B': 'Niemann Pick disease A/B (ASM)',
            'Carnitine acylcarnitine translocase deficiency (CACT)': 'Carnitine-acylcarnitine translocase deficiency (CACT)',
            'Carnitine palmitoyltransferase type I deficiency (CPT IA)': 'Carnitine palmitoyltransferase type I deficiency (CPT-IA)',
            'Carnitine palmitoyltransferase type II deficiency (CPT II)': 'Carnitine palmitoyltransferase type II deficiency (CPT-II)',
            'Citrullinemia type I (CIT)': 'Citrullinemia type I (CIT-I)',
            'Citrullinemia type II (CIT II)': 'Citrullinemia type II (CIT-II)',
            'Glutaric acidemia type I (GA1)': 'Glutaric acidemia type I (GA-1)',
            'Glutaric acidemia type II (GA2)': 'Glutaric acidemia type II (GA-2)',
            'Medium-chain ketoacyl-CoA thiolase deficiency (MCAT)': 'Medium-chain ketoacyl-CoA thiolase deficiency (MCKAT)',
            'Severe combined immunodeficiences (SCID)': 'Severe combined immunodeficiency (SCID)',
            'Tyrosinemia type II (TYR II)': 'Tyrosinemia type II (TYR-II)',
            'Tyrosinemia type III (TYR III)': 'Tyrosinemia type III (TYR-III)',
        }
        na_category = ConditionCategory.objects.get(name='u_cond_na')
        na_conditions = Condition.objects.filter(
            category=na_category).order_by('-ordering').first()
        na_order = 0 if not na_conditions else na_conditions.ordering + 1

        self.cursor.execute("SELECT dictionary_question.field_name, logic_labels_logiclabel.value FROM logic_labels_logiclabel_questions LEFT JOIN logic_labels_logiclabel ON logic_labels_logiclabel.id = logic_labels_logiclabel_questions.logiclabel_id LEFT JOIN dictionary_question ON dictionary_question.id = logic_labels_logiclabel_questions.question_id LEFT JOIN dictionary_sitequestion ON dictionary_sitequestion.question_id = dictionary_question.id WHERE dictionary_sitequestion.current=True AND logic_labels_logiclabel.rule_id <> 10")
        for data in self.cursor.fetchall():
            try:
                name = data[1]

                # check to see if we renamed it
                if name in condition_lookup.keys():
                    name = condition_lookup[name]

                site_questions = SiteQuestion.objects.filter(name=data[0])
                try:
                    condition = Condition.objects.get(name=name)
                except condition.DoesNotExist:
                    # create the condition with no category
                    condition = Condition.objects.create(
                        name=name, label=name, category=na_category, ordering=na_order)

                for site_question in site_questions:
                    site_question.question.conditions.add(condition)
            except:
                print('name: {}'.format(name))
                print(data)
                print(traceback.print_exc())
                sys.exit()

        print('Done.')

    def importQuestionDefinitions(self):
        sys.stdout.write('Importing QuestionDefinitions...')
        sys.stdout.flush()
        self.cursor.execute(
            "SELECT dictionary_question.field_name, dictionary_question.definition FROM dictionary_question WHERE current = True AND dictionary_question.definition IS NOT NULL")
        for data in self.cursor.fetchall():
            question = Question.objects.get(name=data[0])
            definition = Definition.objects.get(definition=data[1])

            question_definition = QuestionDefinition(
                question=question,
                definition=definition,
                version=1
            )
            question_definition.save()

        print('Done.')

    def importChoiceDefinitions(self):
        sys.stdout.write('Importing ChoiceDefinitions...')
        sys.stdout.flush()
        self.cursor.execute(
            "SELECT value, definition FROM dictionary_choice WHERE definition IS NOT NULL")
        for data in self.cursor.fetchall():
            choice = Choice.objects.get(value=data[0])
            definition = Definition.objects.get(definition=data[1])

            choice_definition = ChoiceDefinition(
                choice=choice,
                definition=definition,
                version=1
            )
            choice_definition.save()

        print('Done.')

    def importChoiceCodes(self):
        sys.stdout.write('Importing ChoiceCodes...')
        sys.stdout.flush()
        self.cursor.execute("SELECT dictionary_choice.value, dictionary_code.value, dictionary_codetype.name FROM dictionary_choice_codes JOIN dictionary_choice ON dictionary_choice.id = dictionary_choice_codes.choice_id JOIN dictionary_code ON dictionary_code.id = dictionary_choice_codes.code_id JOIN dictionary_codetype ON dictionary_codetype.id = dictionary_code.code_type_id")
        for data in self.cursor.fetchall():
            code_type = CodeType.objects.get(name=data[2])
            choice = Choice.objects.get(value=data[0])
            code = Code.objects.get(value=data[1], code_type=code_type)

            choice.codes.add(code)

        print('Done.')
