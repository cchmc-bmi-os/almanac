import re
from search.models import Question, SiteQuestionChoice, SiteQuestion
from django.http.response import HttpResponse
import datetime
from almanac import settings
import csv
from django.forms.models import model_to_dict
import sys


def create_node(site, var, op, val, ques_node, connect=None, checked=None):
    try:
        parent_ques = Question.objects.prefetch_related('site_questions').get(name=var)
    except:
        return ques_node, None

    # get the site_question based on
    ques = parent_ques.site_questions.filter(site_id=site).first()

    # text = ques.text
    if var not in ques_node:
        if op != '=' and op != '<>':
            vals = [op + ' ' + val]
        elif op == '<>':
            if not val:
                ft = ques.type
                if ft in ['checkbox', 'dropdown', 'radio', 'matrix']:
                    vals = SiteQuestionChoice.objects.filter(site_question=ques).order_by(
                        'ordering'
                    ).values_list('ordering', flat=True)
                else:
                    vals = "Any Value (can not be blank)"
            else:
                ft = ques.type
                if ft in ['checkbox', 'dropdown', 'radio', 'matrix']:
                    vals = (SiteQuestionChoice.objects.filter(site_question=ques).exclude(
                        ordering=val
                    ).order_by('ordering').values_list('ordering', flat=True))
                else:
                    vals = op + ' ' + vals
        else:
            vals = [val]
        node = {
            'question': ques,
            'answer': vals,
            'connector': connect,
        }
        ques_node[var] = node
        return ques_node, node
    else:
        if connect is not None:
            ques_node[var]['connector'] = connect

        if op != '=':
            ques_node[var]['answer'].append(op + ' ' + val)
            return ques_node, None
        else:
            ques_node[var]['answer'].append(val)
            return ques_node, None


def parse_branching_logic(site, logic):
    ''' Parses a Question's branching logic and returns a list of nodes that
        represent the questions that this question is nested under.
    '''

    variable = re.compile('((?:\[[0-9a-z_A-Z]*\])?\[([0-9a-z_A-Z]+)' +
                          '\(?([0-9]*)\)?\]\s?([=><]+)\s?[\'\"]?(-?[\s0-9]*)[\'\"]?)\s*\)?' + '(\s*[aA][nN][dD]|\s*[oO][rR])?\s*\(?\s*(.*)')
    # orig_str = logic

    # Evaluate the variables in the expression
    rtn_list = []
    ques_node = {}

    var = variable.search(logic)
    remaining = logic
    while var is not None:
        var_name = var.group(2)
        op = var.group(4)
        val = var.group(5)
        checkbox = var.group(3)
        remaining = var.group(7)
        logic_op = var.group(6)

        if logic_op:
            logic_op.upper().strip()
        if checkbox != '':
            ques_node, new_val = create_node(site, var_name, op, checkbox, ques_node, logic_op, val)
        else:
            ques_node, new_val = create_node(site, var_name, op, val, ques_node, logic_op)
        if new_val:
            rtn_list.append(new_val)
        var = variable.search(remaining)
    return rtn_list


def download_redcap(filename, original_data):
    response = HttpResponse(content_type='text/csv')

    filename = '{}-recap_export.csv'.format(datetime.date.today())
    response[
        'Content-Disposition'] = 'attachment; filename="{}"'.format(filename)

    headers = [
        'Variable / Field Name',
        'Form Name',
        'Section Header',
        'Field Type',
        'Field Label',
        'Choices, Calculations, OR Slider Labels',
        'Field Note',
        'Text Validation Type OR Show Slider Number',
        'Text Validation Min',
        'Text Validation Max',
        'Identifier?',
        'Branching Logic (Show field only if...)',
        'Required Field?',
        'Custom Alignment',
        'Question Number (surveys only)',
        'Matrix Group Name',
        'Matrix Ranking?'
    ]
    writer = csv.writer(response, lineterminator='\n')
    writer.writerow(headers)

    previous_section = None
    for item in original_data:
        if type(item) == SiteQuestion:
            write_site_question(writer, item, previous_section, True)
            previous_section = item.form.section
        elif type(item) == list:
            # cast booleans to 'y' or ''
            item[10] = 'y' if item[10] else '';
            item[12] = 'y' if item[12] else '';

            writer.writerow(item)
            previous_section = item[2]

    return response


def write_site_question(writer, question, previous_section, for_data_dictionary):
    url = '{}/view/LPDR'.format(settings.APP_URL)

    data = parse_data_from_site_question(question, previous_section, for_data_dictionary)
    data['type'] = data.get('type').lower()

    if not for_data_dictionary:
        # expand tags
        for tag in data.get('tags'):
            data[tag.get('tag')] = tag

    choices = ['{}, {}'.format(choice.get('id'), choice.get('value')) for choice in data.get('choices')]
    note = '<a href="' + url + '/' + data.get('name') + '" target="_blank"><img src="https://lpdr.nbstrn.org/lpdr-splash-page/Images/open_book.png" height="15" align="top" title="View Data Almanac"></a>'

    writer.writerow([
        data.get('name'),
        data.get('form'),
        data.get('section'),
        data.get('type'),
        data.get('text'),
        data.get('calculation') if data.get('type') == 'calc' else ' | '.join(choices),
        data.get('note') + note if data.get('note') else note,
        data.get('validation'),
        data.get('min_val'),
        data.get('max_val'),
        'y' if data.get('Identifier') else None,
        data.get('branching_logic'),
        'y' if data.get('Required') else None,
        data.get('align'),
        None,
        data.get('matrix_name'),
        None
    ])


def parse_data_from_site_question(question, previous_section, for_data_dictionary):
    q_dict = model_to_dict(question, ['name', 'text', 'min_val', 'max_val', 'validation', 'unknown_val','type', 'calculation', 'align', 'matrix_name', 'note', 'branching_logic'])

    # update the type
    q_dict['type'] = q_dict['type'][0].upper() + q_dict['type'][1:]

    # add the form
    q_dict['form'] = question.form.name

    # get section or blank if same as previous
    q_dict['section'] = None if previous_section == question.form.section else question.form.section

    if not for_data_dictionary:
        if question.form.section:
            q_dict['full_form'] = '{} > {}'.format(question.form.name, question.form.section)
        else:
            q_dict['full_form'] = question.form.name

    # add the definition
    if not for_data_dictionary:
        definition = question.question.definitions.all()
        q_dict['definition'] = definition[0].definition if definition.count() else 'No Definition'
        q_dict['definition_note'] = definition[0].note if definition.count() and definition[0].note else ' '

        # add tags
        q_dict['tags'] = []

        q_dict['tags'].append({'tag': 'Unknown Value', 'value': question.unknown_val})

        if question.max_val:
            q_dict['tags'].append({'tag': 'Max Value', 'value': question.max_val})

        if question.min_val:
            q_dict['tags'].append({'tag': 'Min Value', 'value': question.min_val})

        for tag in question.tags.all():
            q_dict['tags'].append({'tag': tag.label.label, 'value': tag.value})

    # add choices
    q_dict['choices'] = []
    for question_choice in question.site_choices.order_by('ordering'):
        q_dict['choices'].append({'id': question_choice.choice.value, 'value': question_choice.choice.text})

    return q_dict


def setup_progress(text, total):
    sys.stdout.write('%s: %s/%s' % (text, 0, total))
    sys.stdout.flush()


def tick_progress(current, total):
    sys.stdout.write('\b' * (len(str(total)) + len(str(current - 1)) + 1))
    sys.stdout.write('%s/%s' % (current, total))
    sys.stdout.flush()
