import sys

from django.core.management.base import BaseCommand
from search.models import Condition, SiteQuestion, ConditionCategory


class Command(BaseCommand):
    help = 'Updates changes that jen requested'
    cursor = None

    def handle(self, *args, **options):
        sys.stdout.write('Updating database')
        sys.stdout.flush()
        # 1+2.
        # - Rename 'Multiple Carboxylase Deficiency (MCD)' to 'Holocarboxylase Synthase Deficiency'
        # - Apply to all of IBEMC project
        try:
            condition = Condition.objects.get(name='Multiple carboxylase deficiency (MCD)')
            condition.label = 'Holocarboxylase Synthase Deficiency'
            condition.name = 'Holocarboxylase Synthase Deficiency'
            condition.save()
        except BaseException:
            condition = Condition.objects.get(name='Holocarboxylase Synthase Deficiency')
        sys.stdout.write('.')
        sys.stdout.flush()

        for cde in SiteQuestion.objects.filter(site__name='Inborn Errors of Metabolism'):
            cde.question.conditions.add(condition)
        sys.stdout.write('.')
        sys.stdout.flush()

        # 3.
        # - Apply 'Primary Congenital Hypothyroidism' to Arkansas CH
        condition = Condition.objects.get(name='Primary congenital hypothyroidism (CH)')
        for cde in SiteQuestion.objects.filter(site__name='Arkansas CH'):
            cde.question.conditions.add(condition)
        sys.stdout.write('.')
        sys.stdout.flush()

        # 4.
        # - Collapse all 'Congenital adrenal hyperplasia' to one CDE and apply to Arkansas CAH
        first = True
        first_condition = None
        for condition in Condition.objects.filter(name__startswith='Congenital Adrenal Hyperplasia'):
            if first:
                first = False
                condition.label = 'Congenital adrenal hyperplasia'
                condition.name = 'Congenital adrenal hyperplasia'
                condition.save()
                first_condition = condition
                continue

            condition.delete()

        if first_condition:
            for cde in SiteQuestion.objects.filter(site__name='Arkansas CAH'):
                cde.question.conditions.add(first_condition)
        sys.stdout.write('.')
        sys.stdout.flush()

        # 5.
        # - Apply 'S,S Disease (Sickle Cell Anemia)' to Arkansas Hemoglobinopathies
        category = ConditionCategory.objects.get(label='Hemoglobin disorders')
        condition, _ = Condition.objects.get_or_create(name='S,S Disease (Sickle Cell Anemia)', label='S,S Disease (Sickle Cell Anemia)', ordering=22, category=category)
        for cde in SiteQuestion.objects.filter(site__name='Arkansas Hemoglobinopathies'):
            cde.question.conditions.add(condition)
        sys.stdout.write('.')
        sys.stdout.flush()

        # 6.
        # - Apply 'S, βeta-Thalassemia' to Arkansas Hemoglobinopathies
        condition, _ = Condition.objects.get_or_create(name='S, βeta-Thalassemia', label='S, βeta-Thalassemia', ordering=23, category=category)
        for cde in SiteQuestion.objects.filter(site__name='Arkansas Hemoglobinopathies'):
            cde.question.conditions.add(condition)
        sys.stdout.write('.')
        sys.stdout.flush()

        # 7.
        # - Apply 'S,C Disease' to Arkansas Hemoglobinopathies
        condition, _ = Condition.objects.get_or_create(name='S,C Disease', label='S,C Disease', ordering=24, category=category)
        for cde in SiteQuestion.objects.filter(site__name='Arkansas Hemoglobinopathies'):
            cde.question.conditions.add(condition)
        sys.stdout.write('.')
        sys.stdout.flush()

        # 8.
        # - Remove 'Critical Congenital Heart Disease' from conditions
        try:
            ConditionCategory.objects.get(label='Critical Congenital Heart Disease').delete()
        except BaseException:
            pass

        # 9.
        # - Apply 'Cystic Fibrosis' to Arkansas CF
        category = ConditionCategory.objects.get(label='Cystic Fibrosis')
        condition, _ = Condition.objects.get_or_create(name='Cystic Fibrosis', label='Cystic Fibrosis', ordering=1, category=category)
        for cde in SiteQuestion.objects.filter(site__name='Arkansas CF'):
            cde.question.conditions.add(condition)
        sys.stdout.write('.')
        sys.stdout.flush()

        # 10.
        # - Apply 'Hearing Loss' to Arkansas Hearing Screen
        category = ConditionCategory.objects.get(label='Hearing Loss')
        condition, _ = Condition.objects.get_or_create(name='Hearing Loss', label='Hearing Loss', ordering=1, category=category)
        for cde in SiteQuestion.objects.filter(site__name='Arkansas Hearing Screen'):
            cde.question.conditions.add(condition)
        sys.stdout.write('.')
        sys.stdout.write('.')
        sys.stdout.flush()

        # 11.
        # - Apply 'Krabbe disease (GALC)' to Krabbe
        condition = Condition.objects.get(name='Krabbe disease (GALC)')
        for cde in SiteQuestion.objects.filter(site__name='Krabbe'):
            cde.question.conditions.add(condition)
        sys.stdout.write('.')
        sys.stdout.flush()

        # 12.
        # - Remove 'Congenital toxoplasmosis' from conditions
        try:
            Condition.objects.get(name='Congenital toxoplasmosis (TOXO)').delete()
        except BaseException:
            pass
        sys.stdout.write('.')
        sys.stdout.flush()

        # 13.
        # - Remove 'Infectious Diseases' from condition categories
        try:
            ConditionCategory.objects.get(label='Infectious Diseases').delete()
        except BaseException:
            pass
        sys.stdout.write('.')
        sys.stdout.flush()

        # 14.
        # - Change 'SACHDNC Candidate Disorders' to 'Pilot Disorders'
        try:
            category = ConditionCategory.objects.get(label='Congenital toxoplasmosis')
            category.label = 'Pilot Disorders'
            category.save()
        except BaseException:
            pass
        sys.stdout.write('.')
        sys.stdout.flush()

        # 15.
        # - Remove 'Galactose disorders' from condition categories
        try:
            ConditionCategory.objects.get(label='Galactose disorders').delete()
        except BaseException:
            pass
        sys.stdout.write('.')
        sys.stdout.flush()

        # 16.
        # - Remove 'Biotinidase' from condition categories
        try:
            ConditionCategory.objects.get(label='Biotinidase').delete()
        except BaseException:
            pass
        sys.stdout.write('.')
        sys.stdout.flush()

        # 17.
        # - Remove 'Ethylmalonic encephalopathy' from conditions
        try:
            Condition.objects.get(name='Ethylmalonic encephalopathy (EMA)').delete()
        except BaseException:
            pass
        sys.stdout.write('.')
        sys.stdout.flush()

        # 18.
        # - Remove 'Formiminoglutamic acidemia' from conditions
        try:
            Condition.objects.get(name='Formiminoglutamic acidemia (FIGLU)').delete()
        except BaseException:
            pass
        sys.stdout.write('.')
        sys.stdout.flush()

        # 19.
        # - Remove 'Girate atrophy of the retina' from conditions
        try:
            Condition.objects.get(name='Girate atrophy of the retina (Hyper ORN)').delete()
        except BaseException:
            pass
        sys.stdout.write('.')
        sys.stdout.flush()

        # 20.
        # - Remove 'Glucose 6-phospahate dehydrogenas deficiency' from conditions
        try:
            Condition.objects.get(name='Glucose 6-phosphate dehydrogenase deficiency').delete()
        except BaseException:
            pass
        sys.stdout.write('.')
        sys.stdout.flush()

        # 21.
        # - Remove 'Hb*' from conditions if they have 0 cdes
        for condition in Condition.objects.filter(name__startswith='Hb'):
            if condition.questions.count() == 0:
                condition.delete()
        sys.stdout.write('.')
        sys.stdout.flush()

        # 22.
        # - Remove 'Histidenemia' from conditions
        try:
            Condition.objects.get(name='Histidinemia (HIS)').delete()
        except BaseException:
            pass

        # 23.
        # - Remove 'HIV' from conditions
        try:
            Condition.objects.get(name='Human immunodeficiency virus (HIV)').delete()
        except BaseException:
            pass

        # 24.
        # - Remove 'HHH' from conditions
        try:
            Condition.objects.get(name='Hyperornithinemia-Hyperammonemia-Homocitrullinuria syndrome (HHH)').delete()
        except BaseException:
            pass

        # 25.
        # - Remove 'Hyperprolinemia*' from conditions
        try:
            Condition.objects.filter(name__startswith='Hyperprolinemia').delete()
        except BaseException:
            pass

        # 26.
        # - Remove 'Nonketotic hyperglycinemia (glycine encephalopathy) (NKHG)' from conditions
        try:
            Condition.objects.get(name='Nonketotic hyperglycinemia (glycine encephalopathy) (NKHG)').delete()
        except BaseException:
            pass

        # 27.
        # - Remove 'Primary lactic acidemia (LACTIC)' from conditions
        try:
            Condition.objects.get(name='Primary lactic acidemia (LACTIC)').delete()
        except BaseException:
            pass

        # 28.
        # - Remove 'Secondary Congenital Hypothyroidism (CH2)' from conditions
        try:
            Condition.objects.get(name='Secondary Congenital Hypothyroidism (CH2)').delete()
        except BaseException:
            pass

        # 29.
        # - Remove 'Pyruvate carboxylase deficiency' from conditions
        try:
            Condition.objects.get(name='Pyruvate carboxylase deficiency').delete()
        except BaseException:
            pass

        # 30.
        # - Remove 'Thyroid-binding' from conditions
        try:
            Condition.objects.get(name='Thryoid-Binding Globulin Deficiency (TBG)').delete()
        except BaseException:
            pass

        # 31.
        # - Remove 'Valinemia (Hyper VAL)' from conditions
        try:
            Condition.objects.get(name='Valinemia (Hyper VAL)').delete()
        except BaseException:
            pass

        print('Done.')
