from django.core.management.base import BaseCommand
import sys
import csv
import math
from search.models import Site, SiteQuestion, Choice, SiteQuestionChoice
from search.utils.tag_stripper import strip_tags
from search.utils.import_tools import findRootQuestion, convertListToDict, createOrFetchTag, createOrFetchForm, generateCdeModifier


class Command(BaseCommand):
    help = 'Imports a DD into the DA'

    keys = [
        'name',
        'form',
        'section',
        'type',
        'text',
        'choices',
        'note',
        'validation',
        'min_val',
        'max_val',
        'identifier',
        'branching_logic',
        'required',
        'align',
        'question_num',
        'matrix_name',
        'matrix_ranking',
        'annotation',
    ]

    def add_arguments(self, parser):
        parser.add_argument('dd_file', nargs=1, type=str)
        parser.add_argument('--classification', nargs=1,
                            type=str, default=None)

    def handle(self, *args, **options):
        self.classification = options['classification'][
            0] if options['classification'] else None

        # make sure the core is named correctly
        if self.classification == 'Core':
            self.classification = 'NBSTRN Core'

        dd_data = self.loadFromCsv(options['dd_file'][0])
        selected_site = self.createOrDefineSite()
        self.createDaElements(selected_site, dd_data)
        self.verify(selected_site, dd_data)

    def loadFromCsv(self, input_file):
        sys.stdout.write('Parsing and converting file...')
        data = []

        with open(input_file, 'r', encoding='utf-8', errors='replace') as dd_file:
            dd_reader = csv.reader(dd_file)

            skip_header = True
            currentForm = None
            currentSection = None
            for row in dd_reader:
                # skip the first row (header)
                if skip_header is True:
                    skip_header = False
                    continue

                # remove html tags from all fields
                row = map(strip_tags, row)

                row_dict = convertListToDict(row, currentForm, currentSection)

                currentForm = row_dict.get('form')
                currentSection = row_dict.get('section')

                # add to results
                data.append(row_dict)

        print('Done.')
        return data

    def createOrDefineSite(self):
        # get all site ids
        all_sites = Site.objects.all()
        site_ids = ['0'] + list(str(site.id) for site in all_sites)

        # ask user to select a site
        selected_site = None
        while selected_site not in site_ids:
            print('Select a site:')
            print('    (0): New Site')

            # list all the sites
            for site in Site.objects.all():
                print('    ({}): {}'.format(site.id, site.display))

            # ask for which site
            selected_site = input('Enter the number to use: ')

        if selected_site == '0':
            new_site = {
                'name': None,
                'pi': None
            }

            # if user wants a new site
            print ("Enter site information:")
            while not new_site['name']:
                new_site['name'] = input('    Site Name (required): ')

            new_site['pi'] = input('    Site PI (default blank): ')

            if not new_site['pi']:
                new_site['display'] = new_site['name']
            else:
                new_site['display'] = new_site['name'] + ' - ' + new_site['pi']
            new_site['is_live'] = True

            # create new site with the data
            selected_site = Site(
                name=new_site['name'],
                pi=new_site['pi'],
                display=new_site['display'],
                is_live=new_site['is_live']
            )
            selected_site.save()
        else:
            selected_site = Site.objects.get(id=selected_site)

        return selected_site

    def createDaElements(self, site, dd_data):
        dd_step = math.ceil(len(dd_data) / 35)
        sys.stdout.write('Importing data')

        # for each data element
        cnt = 0
        previous_section = None
        for cde in dd_data:
            # step progress
            if cnt % dd_step == 0:
                sys.stdout.write('.')
                sys.stdout.flush()

            # get the root question
            [root, isNew] = findRootQuestion(site, cde)
            self.shouldSetAsDefault = isNew

            # create the Site Question
            previous_section = self.createSiteQuestion(site, root, cde, cnt, previous_section)

            # increment counter
            cnt += 1

        print('Done. ({} cdes)'.format(cnt))

    def createSiteQuestion(self, site, root, cde, ordering, previous_section):
        if not cde.get('section'):
            section = previous_section
        else:
            section = cde.get('section').strip()

        # fetch form
        form = createOrFetchForm(cde.get('form').strip(), section)
        form = self.handleCustomFormTranslation(form)

        # check for inclusion of modifiers
        cde_modifier = generateCdeModifier(root, cde)
        if cde_modifier:
            # print('Modifier: {}'.format(cde_modifier))
            cde['name'] = '{}__{}'.format(cde.get('name'), cde_modifier)
            # print('CDE: {}'.format(cde['name']))

        # print('CDE: {}'.format(cde.get('name')))
        # print('')

        # ordering increment for conversion from 0 based
        ordering += 1

        # create the site question
        site_question = SiteQuestion(
            site=site,
            form=form,
            question=root,
            name=cde.get('name'),
            text=cde.get('text'),
            type=cde.get('type'),
            note=cde.get('note'),
            min_val=float(cde.get('min_val')) if cde.get('min_val') else None,
            max_val=float(cde.get('max_val')) if cde.get('max_val') else None,
            calculation=cde.get('calculation'),
            ordering=ordering,
            align=cde.get('align'),
            matrix_name=cde.get('matrix_name'),
            unknown_val=None,
            branching_logic=cde.get('branching_logic')
        )
        site_question.save()

        # create choices if exist
        choice_cnt = 1
        if cde.get('choices'):
            for choice in cde.get('choices'):
                # create or find choice
                choice_db = Choice.objects.filter(
                    text=choice.get('text'), value=choice.get('id')).first()
                if not choice_db:
                    choice_db = Choice(
                        text=choice.get('text'),
                        value=choice.get('id')
                    )
                    choice_db.save()

                # add it to question
                question_choice = SiteQuestionChoice(
                    site_question=site_question,
                    choice=choice_db,
                    ordering=choice_cnt
                )
                question_choice.save()

                # increment count
                choice_cnt += 1

        # create the identifier tag
        identifier = True if cde.get('identifier') else False
        tag = createOrFetchTag('Identifier', identifier)
        site_question.tags.add(tag)

        # create the required tag
        required = True if cde.get('required') else False
        tag = createOrFetchTag('Required', required)
        site_question.tags.add(tag)

        if self.shouldSetAsDefault:
            tag = createOrFetchTag('LpdrDefault', True)
            site_question.tags.add(tag)

        if self.classification:
            # create the core tag
            tag = createOrFetchTag('Classification', self.classification)
            site_question.tags.add(tag)

        return section

    def handleCustomFormTranslation(self, form):
        if form.name == 'Ms Ms':
            form.name = 'MS/MS'
        elif form.name == 'Nbs':
            form.name = 'NBS'
        elif form.name == 'Reportable Eventsdeviations':
            form.name = 'Reportable Events/deviations'
        elif form.name == 'State of Nsight notes':
            form.name = 'State of NSIGHT notes'

        # save the form change
        form.save()

        return form

    def verify(self, site, data):
        dd_step = math.ceil(len(data) / 35)
        sys.stdout.write('Verifying data')

        # for each data element
        cnt = 0
        for cde in data:
            # step progress
            if cnt % dd_step == 0:
                sys.stdout.write('.')
                sys.stdout.flush()

            if not SiteQuestion.objects.filter(name=cde.get('name')).first():
                print('Could not find {}'.format(cde.get('name')))
                sys.exit()

            cnt += 1

        print('Done. ({} cdes)'.format(cnt))
