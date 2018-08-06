from search import views
from search.models import SiteQuestion, SiteQuestionChoice
import json
import re
from django.db.models import Q
from django.db import connection


def calculate_diff(data):
    # initial data
    diffs = {
        'different': [],
        'not_found': [],
        'found': [],
        'all': [],
    }

    lookups = {
        '0': 'name',
        '4': 'text',
        '5': 'choices/calculation',
        '7': 'validation',
        '8': 'min_val',
        '9': 'max_val',
    }

    orig_cdes = json.loads(data)
    all_cdes = fetch_all_cdes(orig_cdes)

    skip_header = True
    for cde in orig_cdes:
        if skip_header:
            skip_header = False
            continue

        # strip tags from section
        cde[2] = re.sub('<.*?>', '', cde[2])

        found_cde = None
        if cde[0] and cde[0] in all_cdes.keys():
            found_cde = all_cdes[cde[0]]
        elif cde[4] and cde[4] in all_cdes.keys():
            found_cde = all_cdes[cde[4]]

        # add cde to all
        diffs['all'].append(cde)

        if found_cde:
            differences = []
            for idx, key in lookups.items():
                if key in ['min_val', 'max_val']:
                    if cde[int(idx)] and found_cde[key] and float(cde[int(idx)]) == float(found_cde[key]):
                        differences.append(idx)
                else:
                    if key == 'choices/calculation':
                        key = 'calculation' if found_cde['type'] == 'cacl' else 'choices'

                    if cde[int(idx)] != found_cde[key]:
                        differences.append(idx)

            if len(differences) == 0:
                diffs['found'].append(cde)
            else:
                cursor = connection.cursor()
                cursor.execute(
                    'CREATE EXTENSION IF NOT EXISTS fuzzystrmatch; SELECT search_site_questions.id, search_site_questions.name, search_site_questions.text, search_sites.name, levenshtein(%s, search_site_questions.name) + levenshtein(substring(%s, 0, 255), substring(search_site_questions.text, 0, 255)) as levenshtein FROM search_site_questions JOIN search_sites ON search_sites.id = search_site_questions.site_id WHERE search_sites.is_live = True ORDER BY levenshtein LIMIT 5', [cde[0], cde[4]])
                possible_cdes = cursor.fetchall()

                diffs['different'].append({
                    'uploaded': cde,
                    'database': found_cde,
                    'differences': differences,
                    'possible': list(map(lambda item: {
                        'id': item[0],
                        'name': item[1],
                        'text': item[2],
                        'site': item[3],
                        'similarity': item[4],
                    }, possible_cdes))
                })
        else:
            cursor = connection.cursor()
            cursor.execute(
                'CREATE EXTENSION IF NOT EXISTS fuzzystrmatch; SELECT search_site_questions.id, search_site_questions.name, search_site_questions.text, search_sites.name, levenshtein(%s, search_site_questions.name) + levenshtein(substring(%s, 0, 255), substring(search_site_questions.text, 0, 255)) as levenshtein FROM search_site_questions JOIN search_sites ON search_sites.id = search_site_questions.site_id WHERE search_sites.is_live = True ORDER BY levenshtein LIMIT 5', [cde[0], cde[4]])
            possible_cdes = cursor.fetchall()

            diffs['not_found'].append({
                'uploaded': cde,
                'possible': list(map(lambda item: {
                    'id': item[0],
                    'name': item[1],
                    'text': item[2],
                    'site': item[3],
                    'similarity': item[4],
                }, possible_cdes))
            })

    return diffs


def fetch_all_cdes(data):
    # filter out the cde names
    cdes = [item[0] for item in data[1:]]
    texts = [item[4] for item in data[1:]]

    all_cdes = {}
    site_question_ids = views.base_site_questions.filter(Q(name__in=cdes) | Q(text__in=texts)).values_list('id', flat=True)

    for site_question in SiteQuestion.objects.filter(id__in=site_question_ids):
        data = {
            'name': site_question.name,
            'form': site_question.form.name,
            'section': site_question.form.section,
            'type': site_question.type,
            'text': site_question.text,
            'choices': [],
            'calculation': site_question.calculation,
            'note': site_question.note,
            'validation': site_question.validation,
            'min_val': site_question.min_val,
            'max_val': site_question.max_val,
            'identifier': False,
            'branching_logic': site_question.branching_logic,
            'required': False,
            'align': site_question.align,
            'ordering': site_question.ordering,
            'matrix_name': site_question.matrix_name,
            'matrix_ranking': None,
        }

        if data.get('type') != 'calc':
            # choices
            choices = []
            for sq_choice in SiteQuestionChoice.objects.filter(site_question=site_question).order_by('ordering').values_list('choice__value', 'choice__text'):
                choices.append('{}, {}'.format(sq_choice[0], sq_choice[1]))

            data['choices'] = ' | '.join(choices)

        # tags
        for tag in site_question.tags.filter(Q(label__label='Required') | Q(label__label='Identifier')).values_list('label__label', 'value'):
            data[tag[0].lower()] = tag[1]

        all_cdes[site_question.name] = data
        all_cdes[site_question.text] = data

    return all_cdes
