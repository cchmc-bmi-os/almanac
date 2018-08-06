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
from search.utils.helpers import setup_progress, tick_progress


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
        self.clear_database()
        self.import_users()
        management.call_command('update_conditions')
        self.import_code_types()
        self.import_data()
        self.fix_defaults()

    def clear_database(self):
        management.call_command('setup_data_almanac')

        print('')
        print('Import from Database: POSTGRES')

        # get all the database connection information
        tmp_settings = {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
        }

        defaults = {
            'HOST': 'localhost',
            'PORT': '5432',
            'NAME': 'almanac_lpdr',
            'USER': 'root',
            'PASSWORD': 'secret'
        }

        for key in ['HOST', 'PORT', 'NAME', 'USER', 'PASSWORD']:
            data = ''
            while data == '':
                if key == 'PASSWORD':
                    data = getpass(prompt='  Database PASSWORD: ') or defaults['PASSWORD']
                else:
                    data = input('  Database {}: '.format(key)) or defaults[key]

                if data == '':
                    print('Please enter a {}'.format(key.lower()))

            tmp_settings[key] = data

        # save the updated information
        connections.databases['old'] = tmp_settings

        # connect to the old database
        self.cursor = connections['old'].cursor()
        print('')

    def import_users(self):
        self.cursor.execute("SELECT * FROM public.auth_user")
        users = self.dictfetchall()
        total = len(users)
        setup_progress('Importing Users', total)

        cnt = 1
        for data in users:
            try:
                username = data.get('username').lower()

                if 'user' not in username:
                    user = User.objects.create(
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
            except IntegrityError:
                pass

            tick_progress(cnt, total)
            cnt += 1

        print(' - Done.')

    def import_code_types(self):
        self.cursor.execute('SELECT dct.*, ds.name AS source_name, ds.address AS source_address FROM dictionary_codetype AS dct LEFT JOIN dictionary_source AS ds ON ds.id = dct.source_id')
        data = self.dictfetchall()
        total = len(data)
        setup_progress('Importing CodeTypes', total)

        cnt = 1
        for code_type in data:
            # create the source if exists
            source = None if code_type.get('source_name') is None else Source.objects.get_or_create(
                name=code_type.get('source_name'),
                address=code_type.get('source_address')
            )

            # create code
            CodeType.objects.create(
                name=code_type.get('name'),
                description=code_type.get('description'),
                base_url=code_type.get('base_url'),
                note=code_type.get('note'),
                source=source[0]
            )

            tick_progress(cnt, total)
            cnt += 1

        print(' - Done.')

    def import_data(self):
        self.cursor.execute("SELECT dictionary_site.name AS site, dictionary_site.project_pi AS site_pi, dictionary_site.live, dictionary_form.name AS form, dictionary_form.section AS section,  dictionary_question.field_name, dictionary_question.field_text, dictionary_question.field_type, dictionary_question.field_note, dictionary_question.min_val, dictionary_question.max_val, dictionary_question.calculation, dictionary_question.order_number, dictionary_question.align, dictionary_question.matrix_name, dictionary_question.unknown, dictionary_sitequestion.branching_logic, dictionary_question.identifier, dictionary_question.required, dictionary_siteform.order AS form_order, dictionary_siteform.section_order, dictionary_question.definition, dictionary_question.definition_note, dictionary_source.name AS definition_source, dictionary_source.address AS definition_source_address, dictionary_sitequestion.question_id FROM dictionary_sitequestion LEFT JOIN dictionary_site ON dictionary_site.id = dictionary_sitequestion.site_id LEFT JOIN dictionary_siteform ON dictionary_siteform.id = dictionary_sitequestion.site_form_id LEFT JOIN dictionary_question ON dictionary_question.id = dictionary_sitequestion.question_id LEFT JOIN dictionary_form ON dictionary_form.id = dictionary_siteform.form_id LEFT JOIN dictionary_source ON dictionary_source.id = dictionary_question.definition_source_id WHERE dictionary_sitequestion.current = True AND dictionary_site.live = True ORDER BY dictionary_siteform.order, dictionary_siteform.section_order")
        data = self.dictfetchall()
        total = len(data)
        setup_progress('Importing Questions', total)

        site_display_lookup = {
            'IBEMC': 'Inborn Errors of Metabolism',
            'University of Utah': 'Spinal Muscular Atrophy',
            'Mount Sinai': 'Mount Sinai',
        }

        question_ordering = {}

        cnt = 1
        for row in data:
            # get or create the site
            site = Site.objects.get_or_create(
                name=row.get('site'),
                display=site_display_lookup[row.get('site')] if row.get('site') in site_display_lookup else row.get('site'),
                pi=row.get('site_pi'),
                is_live=row.get('live')
            )
            site = site[0]

            # add the site in the question ordering dict
            if site.name not in question_ordering:
                question_ordering[site.name] = 1

            # get or create the form
            form = Form.objects.get_or_create(
                name=row.get('form', None),
                section=row.get('section', None)
            )
            form = form[0]

            # get or create root question
            question = Question.objects.get_or_create(
                name=row.get('field_name')
            )

            # if its created then its the default question
            is_default_question = question[1]
            question = question[0]

            site_question = SiteQuestion.objects.create(
                site=site,
                form=form,
                question=question,
                name=row.get('field_name'),
                text=row.get('field_text'),
                type=row.get('field_type'),
                note=row.get('field_note'),
                min_val=row.get('min_val'),
                max_val=row.get('max_val'),
                calculation=row.get('calculation'),
                ordering=question_ordering[site.name],
                align=row.get('align'),
                matrix_name=row.get('matrix_name'),
                unknown_val=row.get('unknown'),
                branching_logic=row.get('branching_logic')
            )

            # create the nessecary tags
            self.create_tags(row, is_default_question, site_question)

            # create the question definition
            self.create_question_definition(row, question)

            # create the choices
            self.create_choices(question, site_question, row.get('question_id'))

            # create the codes
            self.create_question_codes(question, row.get('question_id'))

            # create the conditions
            self.create_question_conditions(question, row.get('question_id'))

            question_ordering[site.name] += 1
            tick_progress(cnt, total)
            cnt += 1

        print(' - Done.')

    def create_tags(self, row, is_default_question, site_question):
        # add tags
        tags = [
            {'label': 'Identifier', 'value': row.get('identifier')},
            {'label': 'Required', 'value': row.get('required')},
            {'label': 'LpdrDefault', 'value': is_default_question},
        ]

        for tag in tags:
            tag_label = TagLabel.objects.get(label=tag.get('label'))

            # create the tag
            new_tag = Tag.objects.get_or_create(
                value=tag.get('value'),
                label=tag_label,
            )

            # add the tag
            site_question.tags.add(new_tag[0])

    def create_question_definition(self, row, question):
        # if the question has a definition add it
        if row.get('definition') is not None:
            # create the source if exists
            source = None if row.get('definition_source') is None else Source.objects.get_or_create(
                name=row.get('definition_source'),
                address=row.get('definition_source_address')
            )[0]

            # create the definition
            definition = Definition.objects.get_or_create(
                definition=row.get('definition'),
                note=row.get('definition_note', None),
                source=source
            )[0]

            # create the question definition link with version
            QuestionDefinition.objects.create(
                version=1,
                definition=definition,
                question=question
            )

    def create_choices(self, question, site_question, question_id):
        self.cursor.execute("SELECT dc.*, ds.name as definition_source, ds.address as definition_source_address FROM dictionary_choice AS dc LEFT JOIN dictionary_source AS ds ON ds.id = dc.definition_source_id WHERE question_id = {} ORDER BY order_number".format(question_id))

        for choice in self.dictfetchall():
            # get or create the choice
            db_choice = Choice.objects.get_or_create(
                text=choice.get('value'),
                value=int(choice.get('order_number'))
            )[0]

            # create definition if exists
            if choice.get('definition') is not None:
                # create the source if exists
                source = None if choice.get('definition_source') is None else Source.objects.get_or_create(
                    name=choice.get('definition_source'),
                    address=choice.get('definition_source_address')
                )[0]

                # create the definition
                definition = Definition.objects.get_or_create(
                    definition=choice.get('definition'),
                    note=choice.get('definition_note', None),
                    source=source
                )[0]

                ChoiceDefinition.objects.create(
                    choice=db_choice,
                    definition=definition,
                    version=1
                )

            # create and add codes if exist
            self.cursor.execute("SELECT * FROM dictionary_code WHERE id IN (SELECT code_id FROM dictionary_choice_codes WHERE choice_id = {})".format(choice.get('id')))
            for code in self.dictfetchall():
                code_type = CodeType.objects.get(id=code.get('code_type_id'))
                db_code = Code.objects.get_or_create(
                    value=code.get('value'),
                    note=code.get('note'),
                    code_type=code_type
                )[0]

                # add the code
                db_choice.codes.add(db_code)

            # add the mapping
            SiteQuestionChoice.objects.create(
                site_question=site_question,
                choice=db_choice,
                ordering=int(choice.get('order_number'))
            )

    def create_question_codes(self, question, question_id):
        # create and add codes if exist
        self.cursor.execute("SELECT * FROM dictionary_code WHERE id IN (SELECT code_id FROM dictionary_question_codes WHERE question_id = {})".format(question_id))
        for code in self.dictfetchall():
            code_type = CodeType.objects.get(id=code.get('code_type_id'))
            db_code = Code.objects.get_or_create(
                value=code.get('value'),
                note=code.get('note'),
                code_type=code_type
            )[0]

            # add the code
            question.codes.add(db_code)

    def create_question_conditions(self, question, original_question_id):
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
            'Tyrosinemia type I (TYR I)': 'Tyrosinemia type I (TYR-I)',
            'Tyrosinemia type II (TYR II)': 'Tyrosinemia type II (TYR-II)',
            'Tyrosinemia type III (TYR III)': 'Tyrosinemia type III (TYR-III)',
            '2, 4-Dienoyl-CoA reductase deficiency (DE RED)': '2, 4-Dienoyl-CoA reductase deficiency (DE-RED)',
            'Classic galactosemia (GALT)': 'Classical galactosemia (GALT)',
            'Benign Hyperphenylalaninemia (H-PHE)': 'Hyperphenylalaninemia (variant, benign) (H-PHE)',
            'Biopterin defect in cofactor biosynthesis (BIOPT BS)': 'Disorders of biopterin biosynthesis (BIOPT BS)',
            'Biopterin defect in cofactor regeneration (BIOPT REG)': 'Disorders of biopterin regeneration (BIOPT REG)',
            'Classic Phenylketonuria (PKU)': 'Phenylketonuria (PKU)',
            'Medium/short-chain L-3-hydroxyacyl-CoA dehydrogenase deficiency (M/SCHAD)': 'Short-chain L-3-hydroxyacyl-CoA dehydrogenase deficiency (SCHAD)',
            'Holocarboxylase synthetase deficiency (MCD)': 'Multiple carboxylase deficiency (MCD)',
        }

        self.cursor.execute("SELECT ll.* FROM logic_labels_logiclabel AS ll LEFT JOIN logic_labels_logiclabel_questions AS llq ON llq.logiclabel_id = ll.id WHERE llq.question_id = {}".format(original_question_id))
        for condition in self.dictfetchall():
            try:
                norm_condition = condition_lookup[condition.get('value')] if condition.get('value') in condition_lookup else condition.get('value')
                db_condition = Condition.objects.get(name=norm_condition)
                question.conditions.add(db_condition)
            except:
                if condition.get('rule_id') == 10:
                    pass
                else:
                    print(condition)
                    sys.exit()

    def fix_defaults(self):
        question_len = Question.objects.count()
        questions = Question.objects.prefetch_related('site_questions').all()

        setup_progress('Fixing default questions', question_len)

        cnt = 1
        for question in questions:
            needs_fix = False
            found_site_questions = []

            for site_question in question.site_questions.all():
                is_default = site_question.tags.filter(label__label='LpdrDefault', value=True).count() > 0
                if site_question.site.name == 'IBEMC':
                    # flag needs fixed
                    needs_fix = not is_default

                found_site_questions.append(site_question)

            if needs_fix:
                # if IBEMC set default, else remove default
                for site_question in found_site_questions:
                    # update the default tag
                    default_tag = site_question.tags.filter(label__label='LpdrDefault').first()
                    default_tag.value = site_question.site.name == 'IBEMC'
                    default_tag.save()

            tick_progress(cnt, question_len)
            cnt += 1
