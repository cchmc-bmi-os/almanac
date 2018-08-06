import re
from search.models import SiteQuestion, Question, Site, Form, Choice, SiteQuestionChoice, TagLabel, Tag
from review.models import ReviewVersion
import json
import sys
from django.conf import settings


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


def convert_list_to_dict(cde, current_form=None, section=None):
    # convert the list into a dict with the specified keys
    row_dict = dict(zip(keys, cde))
    row_dict['calculation'] = None

    # set section if not empty
    if row_dict['section']:
        section = row_dict['section']
    elif row_dict['form'] == current_form:
        row_dict['section'] = section

    # set the current form for next row
    current_form = row_dict['form']

    # titleize the form name
    row_dict['form'] = row_dict['form'].replace('_', ' ').title()

    # convet min to floats
    row_dict['min_val'] = None if not row_dict['min_val'] else float(row_dict['min_val'].strip())

    # convet max to floats
    row_dict['max_val'] = None if not row_dict['max_val'] else float(row_dict['max_val'].strip())

    # handle calculated fields
    if row_dict['type'] == 'calc':
        row_dict['calculation'] = row_dict['choices']
        row_dict['choices'] = None

    if row_dict['choices']:
        # convert the choices if any (id: 5) (1, Within normal limits | 2,
        # Abnormal | 3, In progress | 4, Results unavailable)
        choices = []
        for choice in row_dict['choices'].split('|'):
            choice_parts = list(map(str.strip, choice.split(',')))
            choices.append({'id': choice_parts[0].strip(), 'text': ', '.join(
                map(str.strip, choice_parts[1:]))})

        row_dict['choices'] = choices

    return row_dict


def create_site_id_from_name(name):
    name = re.sub(r'\W+', '', name).lower()

    # convert site name to an id
    if len(name) < 8:
        return name
    else:
        return name[:8]


def find_root_question(site, cde, no_create=False):
    # try to find a match
    match = SiteQuestion.objects.filter(
        site=site,
        name=cde.get('name'),
        text=cde.get('text'),
        type=cde.get('type')
    ).first()

    if match:
        # user matches root question
        root = match.question
        isNew = False
    else:
        # build the root question name (remove the modifiers)
        cde_name = re.sub('__.*$', '', cde.get('name'))
        root = Question.objects.filter(name=cde_name).first()
        isNew = True

        if not root and no_create:
            # return cde name if not creating question
            return cde_name
        elif not root:
            # create a new root question
            root = Question(name=cde_name)
            root.save()

    return [root, isNew]


def handle_update_da(site_name, review):
    actions = []

    # try to find the site or create it
    site = Site.objects.filter(name=site_name).first()
    if not site:
        actions.append(
            'Created a <strong>Site</strong> named <strong>' + site_name + '</strong>')
        site = Site(name=site_name, display=site_name, pi='', is_live=True)
        site.save()

    site_suffix = create_site_id_from_name(site_name)

    version = ReviewVersion.objects.filter(review_id=review.id).order_by('-revision').first()
    current_form = None
    current_section = None
    ordering = 1
    for cde in json.loads(version.contents):
        cde_dict = convert_list_to_dict(cde, current_form, current_section)

        # get or create the form
        form = Form.objects.filter(name=cde_dict.get('form'), section=cde_dict.get('section')).first()
        if not form:
            actions.append('Created a <strong>Form</strong> with form <strong>' + cde_dict.get('form') + '</strong> and section <strong>' + cde_dict.get('section') + '</strong>')
            form = Form.objects.create(name=cde_dict.get('form'), section=cde_dict.get('section'))
            form.save()

        # get or create the root question
        root_question = find_root_question({'name': site_name}, cde_dict, no_create=True)
        if type(root_question) == str:
            # create the root question
            actions.append('Created a <strong>Question</strong> named <strong>' + root_question + '</strong>')
            root_question = Question.objects.create(name=root_question)
            root_question.save()

        # find the site question
        site_question = SiteQuestion.objects.filter(
            site=site,
            form=form,
            question=root_question,
            name=cde_dict.get('name') + '__' + site_suffix
        ).first()

        if site_question:
            # update the site question
            site_question.text = cde_dict.get('text')
            site_question.type = cde_dict.get('type')
            site_question.note = cde_dict.get('note')
            site_question.min_val = cde_dict.get('min_val')
            site_question.max_val = cde_dict.get('max_val')
            site_question.calculation = cde_dict.get('calculation')
            site_question.ordering = ordering
            site_question.align = cde_dict.get('align')
            site_question.matrix_name = cde_dict.get('matrix_name')
            site_question.unknown_val = None
            site_question.branching_logic = cde_dict.get('branching_logic')

            actions.append('Updated <strong>SiteQuestion</strong> named <strong>' + root_question.name + '</strong>')
            site_question.save()
        else:
            # create the site question
            site_question = SiteQuestion(
                site=site,
                form=form,
                question=root_question,
                name=cde_dict.get('name') + '__' + site_suffix,
                text=cde_dict.get('text'),
                type=cde_dict.get('type'),
                note=cde_dict.get('note'),
                min_val=cde_dict.get('min_val'),
                max_val=cde_dict.get('max_val'),
                calculation=cde_dict.get('calculation'),
                ordering=ordering,
                align=cde_dict.get('align'),
                matrix_name=cde_dict.get('matrix_name'),
                unknown_val=None,
                branching_logic=cde_dict.get('branching_logic')
            )
            actions.append('Created a <strong>SiteQuestion</strong> named <strong>' + root_question.name + '</strong>')
            site_question.save()

            # create choices if exist
            choice_cnt = 1
            if cde_dict.get('choices'):
                for choice in cde_dict.get('choices'):
                    # create or find choice
                    choice_db = Choice.objects.filter(text=choice.get('text'), value=choice.get('id')).first()
                    if not choice_db:
                        choice_db = Choice(
                            text=choice.get('text'),
                            value=choice.get('id')
                        )

                        actions.append('Created a <strong>Choice</strong> with <strong>' + choice.get('id') + ': ' + choice.get('text') + '</strong>')
                        choice_db.save()

                    # add it to question
                    question_choice = SiteQuestionChoice(
                        site_question=site_question,
                        choice=choice_db,
                        ordering=choice_cnt
                    )
                    actions.append('Assigned <strong>Choice</strong> ' + choice.get('id') + ': ' + choice.get('text') + ' to question <strong>' + root_question.name + '</strong>')
                    question_choice.save()

                    # increment count
                    choice_cnt += 1

        # create the identifier tag
        identifier = True if cde_dict.get('identifier') else False
        tag = create_or_fetch_tag('Identifier', identifier)
        text = 'an Identifier' if identifier else 'not an Identifier'
        actions.append('Marking <strong>SiteQuestion</strong> as ' + text)
        site_question.tags.add(tag)

        # create the required tag
        required = True if cde_dict.get('required') else False
        tag = create_or_fetch_tag('Required', required)
        text = 'Required' if required else 'not Required'
        actions.append('Marking <strong>SiteQuestion</strong> as ' + text)
        site_question.tags.add(tag)

        # set data for next cde
        current_form = cde_dict.get('form')
        current_section = cde_dict.get('section')
        ordering += 1

    return json.dumps(actions)


def create_or_fetch_form(form, section):
    if form == 'Ms Ms':
        form = 'MS/MS'
    elif form == 'Nbs':
        form = 'NBS'
    elif form == 'Reportable Eventsdeviations':
        form = 'Reportable Events/deviations'
    elif form == 'State of Nsight notes':
        form = 'State of NSIGHT notes'

    return Form.objects.get_or_create(name=form, section=section)[0]


def create_or_fetch_tag(label, value):
    # find the label
    db_label = TagLabel.objects.get(label=label)

    # try to find the tag
    return Tag.objects.get_or_create(value=value, label=db_label)[0]


def generate_cde_modifier(root, cde):
    form = cde.get('form')
    section = cde.get('section')
    default_site_question = None
    needs_modifier = False

    # find the default question
    for site_question in root.site_questions.order_by('site_id').all():
        # default to first found
        if default_site_question is None:
            default_site_question = site_question

        # if it is the default set the question and break
        for tag in site_question.tags.all():
            if tag.label.label == 'LpdrDefault':
                default_site_question = site_question
                break

    if default_site_question:
        # calculate if need modifier
        needs_modifier = form != default_site_question.form.name or section != default_site_question.form.section

    modifier = None
    # calculate modifier if needed
    if needs_modifier:
        combined_form = '{} {}'.format(form, section)
        first_letters = [i[0] for i in combined_form.lower().split()]
        modifier = ''.join(first_letters)

    return modifier


def setup_progress(text, total):
    sys.stdout.write('%s: %s/%s' % (text, 0, total))
    sys.stdout.flush()


def tick_progress(current, total):
    sys.stdout.write('\b' * (len(str(total)) + len(str(current - 1)) + 1))
    sys.stdout.write('%s/%s' % (current, total))
    sys.stdout.flush()


def create_site_question(site, root, cde, ordering, previous_section, is_default, classification):
    if not cde.get('section'):
        section = previous_section
    else:
        section = cde.get('section').strip()

    # fetch form
    form = create_or_fetch_form(cde.get('form').strip(), section)

    # check for inclusion of modifiers
    cde_modifier = generate_cde_modifier(root, cde)
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
        validation=cde.get('validation'),
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
            choice_db = Choice.objects.filter(text=choice.get('text'), value=choice.get('id')).first()
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
    tag = create_or_fetch_tag('Identifier', identifier)
    site_question.tags.add(tag)

    # create the required tag
    required = True if cde.get('required') else False
    tag = create_or_fetch_tag('Required', required)
    site_question.tags.add(tag)

    if is_default:
        tag = create_or_fetch_tag('LpdrDefault', True)
        site_question.tags.add(tag)

    if classification:
        # create the core tag
        tag = create_or_fetch_tag('Classification', classification)
        site_question.tags.add(tag)

    return section


def setup_tags():
    sys.stdout.write('Creating question tags...')
    sys.stdout.flush()

    labels = [
        {'label': 'VarStatus', 'type': 'text', 'description': 'Variable status. This status reflects the status of the variable as it pertains to the search interface.  Consensus - reviewed by CIG and disease specific workgroup where applicable, Draft  - NBSTRN developed and not yet CIG reviewed, New = Researcher generated not reviewed by CIG yet, Retired = past consensus CDE no longer in use'},
        {'label': 'LpdrDefault', 'type': 'boolean',
            'description': 'Indicates a default LPDR variable when more than one variable mapped back to a CDE.'},
        {'label': 'PI', 'type': 'text',
            'description': 'Indicates the primary investigator.'},
        {'label': 'Instrument', 'type': 'text',
            'description': 'Standardized collection instruments converted to work in REDCap.'},
        {'label': 'Identifier', 'type': 'boolean',
            'description': 'If the question can be used for identifying a subject/participant and is considered PII.'},
        {'label': 'Required', 'type': 'boolean',
            'description': 'If the question is required to be answered.'},
        {'label': 'Classification', 'type': 'text',
            'description': 'Classification of each data element.'},
        {'label': 'CIGReview', 'type': 'boolean',
            'description': 'Reviewed by the clinical integrations group (required for Core and Core(Required) tag)'},
        {'label': 'GUIDVar', 'type': 'boolean',
            'description': 'Indicates the CDE is used to develop a GUID (nDAR).'},
    ]

    for role in settings.DA_REVIEW_ROLES:
        labels.append({'label': '{}Review'.format(role), 'type': 'boolean', 'description': 'Reviewed by {} (required for Core and Core(Required) tag)'.format(role)})

    for label in labels:
        newLabel = TagLabel(
            label=label.get('label'),
            type=label.get('type'),
            description=label.get('description'),
        )
        newLabel.save()

    print('Done.')
