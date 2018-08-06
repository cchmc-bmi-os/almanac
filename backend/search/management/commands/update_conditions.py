from django.core.management.base import BaseCommand
import sys
from search.models import Condition, ConditionCategory
import os
import json


class Command(BaseCommand):
    help = 'Updates the conditions and condition categories'

    def handle(self, *args, **options):
        self.handleManualUpdates()

        dir_path = os.path.dirname(os.path.realpath(__file__))
        json_file = dir_path + '/conditions.json'

        # check if conditions file exists
        if not os.path.isfile(json_file):
            print('Conditions file is not found')
            print('')
            sys.exit()

        json_data = open(dir_path + '/conditions.json').read()
        try:
            data = json.loads(json_data)

            # update the condition categories
            for category in data.get('categories'):
                category_found = ConditionCategory.objects.filter(
                    name=category.get('name')).count()

                # create the category if not found
                if category_found == 0:
                    category_obj = ConditionCategory.objects.create(
                        label=category.get('label'),
                        name=category.get('name'),
                        ordering=category.get('ordering')
                    )
                    category_obj.save()

            # update the conditions
            for condition_category in data.get('conditions'):
                category = ConditionCategory.objects.get(
                    name=condition_category)

                for condition in data.get('conditions').get(condition_category):
                    condition_found = Condition.objects.filter(
                        name=condition.get('name')).count()

                    # create the condition if not found
                    if condition_found == 0:
                        condition_obj = Condition.objects.create(
                            label=condition.get('name'),
                            name=condition.get('name'),
                            ordering=condition.get('ordering'),
                            category=category
                        )
                        condition_obj.save()
                    else:
                        # update the category
                        condition = Condition.objects.filter(
                            name=condition.get('name')).first()

                        # save the new category
                        condition.category = category
                        condition.save()
        except:
            print('Could not parse conditions file')
            print('')
            sys.exit()

    def handleManualUpdates(self):
        updates = [
            {'orig': 'Fabry', 'mod': 'Fabry disease (GLA)'},
            {'orig': 'Niemann Pick Types A and B',
                'mod': 'Niemann Pick disease A/B (ASM)'},
            {'orig': '2, 4-Dienoyl-CoA reductase deficiency (DE RED)',
             'mod': '2, 4-Dienoyl-CoA reductase deficiency (De-Red)'},
            {'orig': 'Carnitine acylcarnitine translocase deficiency (CACT)',
             'mod': 'Carnitine-acylcarnitine translocase deficiency (CACT)'},
            {'orig': 'Carnitine palmitoyltransferase type I deficiency (CPT IA)',
             'mod': 'Carnitine palmitoyltransferase type I deficiency (CPT-IA)'},
            {'orig': 'Carnitine palmitoyltransferase type II deficiency (CPT II)',
             'mod': 'Carnitine palmitoyltransferase type II deficiency (CPT-II)'},
            {'orig': 'Citrullinemia type I (CIT)',
             'mod': 'Citrullinemia type I (CIT-I)'},
            {'orig': 'Citrullinemia type II (CIT II)',
             'mod': 'Citrullinemia type II (CIT-II)'},
            {'orig': 'Glutaric acidemia type I (GA1)',
             'mod': 'Glutaric acidemia type I (GA-1)'},
            {'orig': 'Glutaric acidemia type II (GA2)',
             'mod': 'Glutaric acidemia type II (GA-2)'},
            {'orig': 'Medium-chain ketoacyl-CoA thiolase deficiency (MCAT)',
             'mod': 'Medium-chain ketoacyl-CoA thiolase deficiency (MCKAT)'},
            {'orig': 'Severe combined immunodeficiences (SCID)',
             'mod': 'Severe combined immunodeficiency (SCID)'},
            {'orig': 'Tyrosinemia type I (TYR I)',
             'mod': 'Tyrosinemia type I (TYR-1)'},
            {'orig': 'Tyrosinemia type II (TYR II)',
             'mod': 'Tyrosinemia type II (TYR-II)'},
            {'orig': 'Tyrosinemia type III (TYR III)',
             'mod': 'Tyrosinemia type III (TYR-III)'},
        ]

        for update in updates:
            # try to find the update
            condition = Condition.objects.filter(
                name=update.get('orig')).first()

            # update the condition if found
            if condition:
                condition.label = update.get('mod')
                condition.name = update.get('mod')
                condition.save()
