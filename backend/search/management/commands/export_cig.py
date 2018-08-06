from django.core.management.base import BaseCommand
from search.models import SiteQuestion, Site
import csv
import sys
import re
import math


class Command(BaseCommand):
    help = 'Exports the CDE data for the CIG'

    reviewers = {
        'sue_berry': [
            'Argininemia (ARG)',
            'Argininosuccinic aciduria (ASA)',
            'Citrullinemia type I (CIT-I)',
            'Citrullinemia type II (CIT-II)',
            'Methylmalonic acidemia (cobalamin disorders) (CblA,B)',
            'Methylmalonic acidemia (methylmalonyl-CoA mutase) (MUT)',
            'Methylmalonic acidemia with homocystinuria (Cbl C,D)',
            'Propionic acidemia (PROP)',
        ],
        'kathy_swoboda': [
            'Disorders of biopterin biosynthesis (BIOPT BS)',
            'Disorders of biopterin regeneration (BIOPT REG)',
            'Phenylketonuria (PKU)'
        ],
        'janet_thomas': [
            'Hypermethioninemia (MET)',
            'Maple syrup urine disease (MSUD)',
            'Tyrosinemia type I (TYR-I)',
            'Tyrosinemia type II (TYR-II)',
            'Tyrosinemia type III (TYR-III)',
        ],
        'tom_langan': [
            'Carnitine-acylcarnitine translocase deficiency (CACT)',
            'Carnitine palmitoyltransferase type I deficiency (CPT-IA)',
            'Carnitine palmitoyltransferase type II deficiency (CPT-II)',
            'Medium-chain acyl-CoA dehydrogenase deficiency (MCAD)',
            '2, 4-Dienoyl-CoA reductase deficiency (DE-RED)',
            'Carnitine uptake defect/carnitine transport defect (CUD)',
            'Glutaric acidemia type II (GA-2)',
            'Trifunctional protein deficiency (TFP)',
        ],
        'michelle_caggana': [
            'Very long-chain acyl-CoA dehydrogenase deficiency (VLCAD)',
            'Long-chain L-3 hydroxyacyl-CoA dehydrogenase deficiency (LCHAD)',
            'Medium-chain ketoacyl-CoA thiolase deficiency (MCKAT)',
            'Short-chain L-3-hydroxyacyl-CoA dehydrogenase deficiency (SCHAD)',
            'Short-chain acyl-CoA dehydrogenase deficiency (SCAD)',
            'Biotinidase deficiency (BIOT)',
        ],
        'debbie_freedenberg': [
            'Classical galactosemia (GALT)',
            'Galactoepimerase deficiency (GALE)',
            'Galactokinase deficiency (GALK)',
        ]
    }

    def handle(self, *args, **options):
        headers = ['PROJECT(S)', 'DEFINITION', 'IDENTIFIER', 'REQUIRED', 'CLASSIFICATION', 'CONDITIONS', 'VARIABLE NAME', 'FORM NAME', 'SECTION HEADER', 'FIELD TYPE', 'FIELD LABEL', 'CHOICES', 'ORDERING']

        print('Generating CSV files:')

        sites = Site.objects.filter(name='IBEMC').values_list('display', flat=True)

        for reviewer in self.reviewers:
            sys.stdout.write('  For {}: '.format(reviewer.replace('_', ' ').title()))
            sys.stdout.flush()
            filename = 'cig_forms_{}.csv'.format(reviewer)

            with open(filename, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)

                # write the headers
                csvwriter.writerow(headers)

                site_questions = SiteQuestion.objects.filter(question__conditions__name__in=self.reviewers[reviewer], site__name='IBEMC').distinct().prefetch_related('tags', 'tags__label', 'question', 'question__conditions', 'question__definitions', 'site_choices', 'form').order_by('ordering')
                num_questions = site_questions.count()

                # progress bar
                sys.stdout.write('%s/%s' % (0, num_questions))
                sys.stdout.flush()
                # sys.stdout.write('\b' * (len(str(num_questions)) + len(str(0)) + 1))

                cnt = 1
                for site_question in site_questions:
                    definition = site_question.question.definitions.first()
                    tags = {}

                    for tag in site_question.tags.all():
                        tags[tag.label.label] = tag.value

                    choices = []
                    for question_choice in site_question.site_choices.all():
                        choices.append({'id': question_choice.choice.value, 'value': question_choice.choice.text})

                    conditions = [re.search('\(([^)]*)\)[^(]*$', item).group(1) for item in site_question.question.conditions.values_list('name', flat=True)]

                    tmp = [
                        ', '.join(sites),
                        definition.definition if definition else 'No Definition',
                        'Yes' if tags.get('Identifier') == 'True' else 'No',
                        'Yes' if tags.get('Required') == 'True' else 'No',
                        tags.get('Classification') if 'Classification' in tags else 'None',
                        ', '.join(conditions),
                        site_question.question.name,
                        site_question.form.name,
                        site_question.form.section,
                        site_question.type,
                        site_question.text,
                        ' | '.join(['{}, {}'.format(item.get('id'), item.get('value')) for item in choices]),
                        site_question.ordering
                    ]

                    csvwriter.writerow(tmp)

                    sys.stdout.write('\b' * (len(str(num_questions)) + len(str(cnt - 1)) + 1))
                    sys.stdout.write('%s/%s' % (cnt, num_questions))
                    sys.stdout.flush()

                    cnt += 1

            print(' - Done.')
