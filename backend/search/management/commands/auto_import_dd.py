import sys
from os import listdir
from os.path import isfile, join
import re
import csv
import fileinput
import datetime
from getpass import getpass

from django.conf import settings
from django.core import management
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from django.db import transaction, connections
from django.contrib.auth.models import User

from search.utils.import_tools import setup_progress, tick_progress, setup_tags
from search.utils.tag_stripper import strip_tags
from search.models import Site, Condition
from search.utils.import_tools import convert_list_to_dict, find_root_question, create_site_question, create_or_fetch_form, create_or_fetch_tag, generate_cde_modifier


class Command(BaseCommand):
    help = 'Auto Imports all DD files in a directory'

    classifications = {
        'NBSTRN Core': 'NBSTRN Core'
    }

    cursor = None

    def dictfetchall(self):
        "Return all rows from a cursor as a dict"
        columns = [col[0] for col in self.cursor.description]
        return [
            dict(zip(columns, row))
            for row in self.cursor.fetchall()
        ]

    def add_arguments(self, parser):
        parser.add_argument('directory', nargs=1, type=str)

    def handle(self, *args, **options):
        confirm = input('This will clear the database, are you sure (y/N)? ') or 'N'
        if confirm.lower() != 'y':
            print('Import aborted')
            sys.exit()

        self.setup_connection()

        # make sure db is migrated
        sys.stdout.write('Migrating database...')
        sys.stdout.flush()
        management.call_command('migrate')
        print('Done.')

        sys.stdout.write('Clearing database...')
        sys.stdout.flush()
        self.clear_database()
        print('Done.')

        sys.stdout.write('Updating conditions...')
        sys.stdout.flush()
        management.call_command('update_conditions')
        print('Done.')

        setup_tags()

        print('')
        print('Loading DD:')

        directory = options['directory'][0]

        # get all csv files that start with a number
        all_files = [f for f in listdir(directory) if isfile(join(directory, f)) and re.match(r'^\d\d\d-.*\.csv$', f)]

        for dd_file in sorted(all_files):
            # get the site name based on the filename
            m = re.search(r'^\d\d\d-(.*)\.csv$', dd_file)
            if not m:
                raise Exception('Invalid file name')
            site_name = m.group(1).replace('_', ' ').replace('-', '/')

            classification = self.classifications[site_name] if site_name in self.classifications else None

            with open(join(directory, dd_file), errors='ignore') as f:
                # read file length and return to front
                reader = csv.reader(f)
                total = sum(1 for row in reader)
                f.seek(0)
                cnt = 1
                skip_header = True

                # find or create the site
                site = Site.objects.get_or_create(name=site_name, display=site_name, pi='', is_live=True)[0]

                setup_progress('Loading {}'.format(site_name), total)
                with transaction.atomic():
                    # initial form and section
                    current_form = None
                    current_section = None
                    previous_section = None

                    for row in reader:
                        # skip the header
                        if skip_header:
                            skip_header = False
                            cnt += 1
                            continue

                        # remove html tags from all fields
                        row = map(strip_tags, row)

                        # convert row to a dict
                        row_dict = convert_list_to_dict(row, current_form, current_section)

                        # set current form and section
                        current_form = row_dict.get('form')
                        current_section = row_dict.get('section')

                        # get the root question
                        [root, is_default] = find_root_question(site, row_dict)

                        # create the Site Question
                        previous_section = create_site_question(site, root, row_dict, cnt, previous_section, is_default, classification)

                        # add conditions to the question
                        if site_name == 'Inborn Errors of Metabolism':
                            self.create_question_conditions(root)

                        # mark progress
                        tick_progress(cnt, total)
                        cnt += 1

                # finished with file
                print(' - Done')

        self.update_settings()

        # import the LSD conditions
        management.call_command('import_conditions', join(directory, 'conditions/LPDR_LSD_Dataset_conditions.csv'))

        # do the fixes
        management.call_command('fix_sibling_cdes')
        management.call_command('fix_oth_cdes')
        management.call_command('pull_conditions')

    def clear_database(self):
        tables_to_clear = [
            'search_choice_definitions',
            'search_choices',
            'search_choices_codes',
            'search_code_types',
            'search_codes',
            'search_condition_categories',
            'search_conditions',
            'search_definitions',
            'search_forms',
            'search_question_definitions',
            'search_questions',
            'search_questions_codes',
            'search_questions_conditions',
            'search_site_question_choices',
            'search_site_questions',
            'search_site_questions_tags',
            'search_sites',
            'search_sources',
            'search_tag_labels',
            'search_tags',
        ]
        with connections['default'].cursor() as cursor:
            cursor.execute('TRUNCATE TABLE {} RESTART IDENTITY CASCADE'.format(', '.join(tables_to_clear)))

    def update_settings(self):
        file_path = join(settings.BASE_DIR, 'almanac', 'settings_local.py')

        # loop over the file
        for line in fileinput.input(file_path, inplace=True):
            if line.startswith('DATA_LOAD_DATE'):
                print('DATA_LOAD_DATE = \'{}\''.format(datetime.datetime.now().date()))
            else:
                print(line.rstrip())

    def setup_connection(self):
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

    def create_question_conditions(self, question):
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

        self.cursor.execute("SELECT ll.* FROM logic_labels_logiclabel AS ll LEFT JOIN logic_labels_logiclabel_questions AS llq ON llq.logiclabel_id = ll.id LEFT JOIN dictionary_question AS dq ON dq.id = llq.question_id WHERE dq.field_name = '{}'".format(question.name))
        for condition in self.dictfetchall():
            try:
                norm_condition = condition_lookup[condition.get('value')] if condition.get('value') in condition_lookup else condition.get('value')
                [db_condition, _] = Condition.objects.get_or_create(name=norm_condition)
                question.conditions.add(db_condition)
            except BaseException:
                if condition.get('rule_id') == 10:
                    pass
                else:
                    print(condition)
                    sys.exit()
