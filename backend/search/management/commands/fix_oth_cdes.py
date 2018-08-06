from django.core.management.base import BaseCommand
from search.models import Question


class Command(BaseCommand):
    help = 'Fixes the _oth cdes to pull their parent conditions for mapping'

    def handle(self, *args, **options):
        # get the sib_8 cde conditions
        oth_cdes = Question.objects.filter(name__endswith='_oth')

        for oth_cde in oth_cdes:
            if oth_cde.conditions.count() == 0:
                print('Checking {}:'.format(oth_cde.name))
                parent_search = oth_cde.name.replace('_oth', '')
                if oth_cde.name == 'mental_health_prov_oth':
                    parent_search = 'mental_health_provider'

                parent = Question.objects.filter(name=parent_search).first()

                if parent.conditions.count() > 0:
                    print('Applying parent conditions')
                    oth_cde.conditions.add(*parent.conditions.all())
                else:
                    for sq in parent.site_questions.all():
                        print(sq.name, sq.site)

                    print('Parent has no conditions: {} -> {}'.format(oth_cde, parent))
