from django.core.management.base import BaseCommand
from search.models import SiteQuestion, Tag, TagLabel
import csv


class Command(BaseCommand):
    help = 'Fixes the is_default flag to the first occurance of the root cde'

    def handle(self, *args, **options):
        questions = []
        tag_label = TagLabel.objects.get(label='LpdrDefault')

        for site_question in SiteQuestion.objects.prefetch_related('question').order_by('id'):
            is_default = site_question.question.name not in questions
            lpdr_default = site_question.tags.filter(label__label='LpdrDefault').first()

            if is_default and not lpdr_default:
                # add the is_default flag
                print('Adding default flag to {}'.format(site_question.name))
                # get or create the tag and add it to the site question
                tag, _ = Tag.objects.get_or_create(label=tag_label, value=True)
                site_question.tags.add(tag)
            elif not is_default and lpdr_default:
                # remove the default flag
                print('Removing default flag from {}'.format(site_question.name))
                site_question.tags.remove(lpdr_default)
            # else:
            #     if lpdr_default:
            #         print('Already is marked as default for {}'.format(site_question.name))
            #     else:
            #         print('Already is marked as NOT default for {}'.format(site_question.name))

            questions.append(site_question.question.name)
