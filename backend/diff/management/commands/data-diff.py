from django.core.management.base import BaseCommand
import sys
import os
import csv


class Command(BaseCommand):
    help = 'Calculates a diff report from two REDCap Data Dictionaries'

    source_data_one = {}
    source_data_two = {}
    diff_data = {
        'found': [],
        'different': [],
        'missing': []
    }

    def add_arguments(self, parser):
        parser.add_argument('destination', nargs=1, type=str)
        parser.add_argument('first_file', nargs=1, type=str)
        parser.add_argument('second_file', nargs=1, type=str)

    def handle(self, *args, **options):
        self.calculateDiff(options['first_file'][0], options['second_file'][0])
        self.report(options['destination'][0])

    def calculateDiff(self, first_file, second_file):
        sys.stdout.write('Calculating differences...')

        # load the first file data
        with open(first_file) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                self.source_data_one[row[0]] = row

        # load the second file data
        with open(second_file) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                self.source_data_two[row[0]] = row

        # loop through larger file to match ids
        if len(self.source_data_one) >= len(self.source_data_two):
            source_data = self.source_data_one
            target_data = self.source_data_two
        else:
            source_data = self.source_data_two
            target_data = self.source_data_one

        # define the fields requested
        lookups = {
            '4': 'field_text',
            '5': 'choices',
            '8': 'min_val',
            '9': 'max_val'
        }

        for key in source_data:
            if key in target_data.keys():
                different = False
                differences = []

                # check other columns for difference
                for index in lookups:
                    source_value = source_data[key][int(index)].lower().replace(
                        ' ', '') if source_data[key][int(index)] else None
                    target_value = target_data[key][int(index)].lower().replace(
                        ' ', '') if target_data[key][int(index)] else None
                    if source_value != target_value:
                        different = True
                        differences.append({
                            'source': source_data[key],
                            'target': target_data[key]
                        })

                if(different):
                    self.diff_data['different'].append(differences)
                else:
                    self.diff_data['found'].append(source_data[key])
            else:
                self.diff_data['missing'].append(source_data[key])

        print('Done.')

    def report(self, destination):
        print('Results:')
        print('Found: {}'.format(len(self.diff_data['found'])))
        print('Different: {}'.format(len(self.diff_data['different'])))
        print('Missing: {}'.format(len(self.diff_data['missing'])))

        if not os.path.exists(destination):
            os.makedirs(destination)

        # header
        headers = [
            'Variable / Field Name',
            'Form Name',
            'Section Header',
            'Field Type',
            'Field Label Choices, Calculations, OR Slider Labels Field Note',
            'Text Validation Type OR Show Slider Number',
            'Text Validation Min',
            'Text Validation Max Identifier?',
            'Branching Logic (Show field only if...)',
            'Required Field?',
            'Custom Alignment',
            'Question Number (surveys only)',
            'Matrix Group Name',
            'Matrix Ranking?'
        ]

        # write info to csvs
        for dict_key in ['found', 'missing']:
            writer = csv.writer(
                open('{}/{}.csv'.format(destination, dict_key), 'w'))
            writer.writerow(headers)
            writer.writerows(self.diff_data[dict_key])

        # write out differences
        writer = csv.writer(
            open('{}/{}.csv'.format(destination, 'diffreneces'), 'w'))
        writer.writerow(headers)
        for item in self.diff_data['different']:
            writer.writerow(item[0]['source'])
            writer.writerow(item[0]['target'])
            writer.writerow([])
