import os
import csv
import json
import pytz
import shutil
import datetime
import bugsnag
from subprocess import run

from django.http import JsonResponse
from django.conf import settings
from django.db import transaction

from rest_framework import viewsets
from rest_framework.decorators import api_view

from .models import Review, ReviewVersion, ReviewRole
from .utils.diff import calculate_diff
from .serializers import ReviewSerializer, ReviewVersionSerializer, ReviewRoleSerializer

from search.models import SiteQuestion, SiteQuestionChoice, Site, SiteQuestionArchive, SiteQuestionArchiveChoice, Condition
from review.utils.email import send_review_completed_email, send_review_removal_email
from search.utils.helpers import download_redcap
from search.utils.import_tools import handle_update_da, convert_list_to_dict, find_root_question, create_site_question, create_or_fetch_form, create_or_fetch_tag, generate_cde_modifier

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    filter_fields = ('user__id', 'status',)

    def get_queryset(self):
        has_roles = ReviewRole.objects.filter(
            user=self.request.user).count() > 0

        # if the user is staff or they have review roles
        if self.request.user.is_staff or has_roles:
            return Review.objects.order_by('started_at')

        # only display the persons roles
        return Review.objects.filter(user=self.request.user).order_by('started_at')


class ReviewVersionViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewVersionSerializer
    filter_fields = ('review__id',)

    def get_queryset(self):
        has_roles = ReviewRole.objects.filter(user=self.request.user).count() > 0

        # if the user is staff or they have review roles
        if self.request.user.is_staff or has_roles:
            return ReviewVersion.objects.order_by('-revision')

        # only display the persons roles
        return ReviewVersion.objects.filter(review__user=self.request.user).order_by('-revision')


class ReviewRoleViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ReviewRoleSerializer

    def get_queryset(self):
        return ReviewRole.objects.filter(user=self.request.user).order_by('id')


@api_view(['POST'])
def upload(request):
    try:
        user = request.user
        review_name = request.POST.get('name')
        review = Review.objects.filter(user=user, name=review_name)

        # make sure there is no duplicate
        if review:
            return JsonResponse({'success': False, 'message': 'Review name has already been used'})

        work_dir_base = os.path.join(os.path.dirname(__file__), 'tmp')

        if not os.path.isdir(work_dir_base):
            # create the director if it doesn't exist
            os.mkdir(work_dir_base)

        # remove all old uploads for that user
        for item in os.listdir(work_dir_base):
            if user.username in item:
                shutil.rmtree(os.path.join(work_dir_base, item))

        # generate new workdir
        work_dir = os.path.join(work_dir_base, '{}-{}'.format(user.username, datetime.datetime.now().strftime('%Y.%m.%d.%H.%M.%S')))

        # make a directory to store the files
        os.mkdir(work_dir)

        # copy uploaded file to work_dir
        file_path = os.path.join(work_dir, 'file.csv')
        with open(file_path, 'wb+') as destination:
            for chunk in request.FILES['file'].chunks():
                destination.write(chunk)

        # try to convert file to unix line endings
        run(['perl', '-pi', '-e', 's/\r\n|\n|\r/\n/g', file_path])
        # remove any blank lines
        run(['perl', '-pi', '-e', 's/^\n$//g', file_path])

        header = None
        data = []
        with open(file_path, newline='', encoding='utf-8', errors='ignore') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if header is None:
                    header = row

                data.append(row)

        return JsonResponse({
            'success': True,
            'header': header,
            'name': review_name,
            'data': data,
            'location': work_dir.replace(work_dir_base, ''),
        })
    except FileNotFoundError as e:
        bugsnag.notify(e)
        return JsonResponse({'success': False, 'message': 'Could not save file, server error'})
    except Exception as e:
        bugsnag.notify(e)
        return JsonResponse({'success': False, 'message': 'Could not parse file'})


@api_view(['GET'])
def diff(request, review_id):
    try:
        review = Review.objects.get(id=review_id)
        version = ReviewVersion.objects.filter(review=review).order_by('-revision').first()

        # make sure that the revision and the info is what we expect to
        # generete a diff
        if version.revision == '1' and version.info == 'Uploaded DD':
            return JsonResponse({'success': False, 'message': 'The review is not in a state to calculate the diff'})

        diffs = calculate_diff(version.contents)
        diff_version = ReviewVersion.objects.create(
            review=review,
            revision=2,
            contents=json.dumps(diffs),
            summary=None,
            actions=None,
            info='Data dictionary difference',
            is_locked=True
        )
        diff_version.save()

        diff_version = ReviewVersion.objects.create(
            review=review,
            revision=3,
            contents=json.dumps(diffs),
            summary=None,
            actions=None,
            info='Grantee Annotation',
            is_locked=False
        )
        diff_version.save()

        # lock the previous version
        version.is_locked = True
        version.save()

        # update the review status
        review.status = 'Grantee Review'
        review.save()

        return JsonResponse(diffs, safe=True)
    except Exception as e:
        print(e)
        bugsnag.notify(e)
        return JsonResponse({'success': False, 'message': 'Unkown error occurred'})


def convert_to_data(cde):
    data = [
        cde.name,
        cde.form.name,
        cde.form.section,
        cde.type,
        cde.text,
        cde.calculation,
        cde.note,
        cde.validation,
        cde.min_val,
        cde.max_val,
        False,
        cde.branching_logic,
        False,
        cde.align,
        cde.ordering,
        cde.matrix_name,
        None,
    ]

    # handle choices
    choices = []
    for sq_choice in SiteQuestionChoice.objects.filter(site_question=cde).order_by('ordering').values_list('choice__value', 'choice__text'):
        choices.append('{}, {}'.format(sq_choice[0], sq_choice[1]))

    data[5] = ' | '.join(choices)

    return data


@api_view(['GET'])
def final_calculation(request, review_id):
    version = ReviewVersion.objects.filter(
        review_id=review_id).order_by('-revision').first()

    # if it is locked error out
    if version.is_locked:
        return JsonResponse({'errors': [{'code': 400, 'title': 'Version is locked, cannot modify'}]}, status=400, safe=True)

    actions = json.loads(version.actions)
    new_contents = []
    for item in json.loads(version.contents).get('all'):
        append_after = None
        append_item = True

        if actions and item[0] in actions:
            for action in actions[item[0]]:
                # ignore the not accepted actions
                if not action.get('accepted', True):
                    continue

                if action.get('operation') == 'add_existing':
                    # fetch the cde from database
                    cde = SiteQuestion.objects.get(
                        name=action.get('additional'), site__is_live=True)

                    if action.get('location') == 'before':
                        # add before current item
                        new_contents.append(convert_to_data(cde))
                    else:
                        # add after current item
                        append_after = convert_to_data(cde)
                elif action.get('operation') == 'add_new':
                    # send to CIG stuff
                    # TBD
                    pass
                elif action.get('operation') == 'add_note':
                    item[6] = action.get('additional')
                elif action.get('operation') == 'delete' or action.get('operation') == 'multiples_found':
                    # do nothing
                    append_item = False
                    pass
                elif action.get('operation') == 'update_label':
                    # update the label of the question
                    item[4] = action.get('additional')
                elif action.get('operation') == 'update_branching':
                    # update the branching logic
                    item[11] = action.get('additional')
                elif action.get('operation') == 'update_control':
                    # update the field type
                    item[3] = action.get('additional')
                elif action.get('operation') == 'update_choices':
                    item[5] = action.get('additional')
                elif action.get('operation') == 'update_da':
                    # send to CIG stuff
                    # TBD
                    pass
                elif action.get('operation') == 'rename':
                    # rename the CDE
                    item[0] = action.get('additional')
                elif action.get('operation') == 'replace':
                    # fetch the cde from database
                    cdes = SiteQuestion.objects.filter(
                        name=action.get('additional'), site__is_live=True)

                    found_core = False
                    for cde in cdes:
                        if cde.site.name == 'NBSTRN Core':
                            found_core = True
                            break

                    # choose the first entry if we didn't find a core element
                    if not found_core:
                        cde = cdes[0]

                    item = convert_to_data(cde)

            # add the modified item
            if append_item:
                new_contents.append(item)

            # add the data after if needed
            if append_after:
                new_contents.append(append_after)
        else:
            new_contents.append(item)

    # create final version
    final_version = ReviewVersion.objects.create(
        review=version.review,
        revision=version.revision + 1,
        contents=json.dumps(new_contents),
        summary=None,
        actions=json.dumps(json.loads(version.contents).get('defaultConditions')),
        info='Final Data Dictionary',
        is_locked=True
    )
    final_version.save()

    # set review completed at date
    version.review.status = 'Completed'
    version.review.completed_at = datetime.datetime.now()
    version.review.save()

    send_review_completed_email(request.user, final_version)

    # lock the previous one
    version.is_locked = True
    version.save()

    return JsonResponse({'status': 'ok'}, safe=True)


@api_view(['GET'])
def export_redcap(request, review_id):
    version = ReviewVersion.objects.filter(
        review_id=review_id).order_by('-revision').first()
    return download_redcap('final_dd', json.loads(version.contents))


@api_view(['GET'])
def update_da(request, review_id, site_id):
    # make sure user is admin
    is_admin = False
    for role in request.user.review_role.all():
        if role.role == settings.DA_REVIEW_ADMIN_ROLE:
            is_admin = True

    if not is_admin:
        return JsonResponse({'errors': [{'code': 403, 'title': 'You are not allowed to download the sql'}]}, status=403, safe=True)

    # add all of the site questions from review
    latest_version = ReviewVersion.objects.filter(review_id=review_id).order_by('-revision').first()
    if latest_version.updated_da_on is not None:
        return JsonResponse({'errors': [{'code': 401, 'title': 'This review has already been updated into the DA'}]}, status=401, safe=True)

    # get site object
    site = Site.objects.get(id=site_id)

    # copy all site questions to archive
    archived_at = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
    for site_question in SiteQuestion.objects.filter(site=site):
        data = {'date_archived': archived_at}

        # copy fields over
        for fld in site_question._meta.fields:
            if fld.name != 'id':
                data[fld.name] = getattr(site_question, fld.name)

        # copy site question data
        archived_site_question = SiteQuestionArchive.objects.create(**data)

        # copy tags
        archived_site_question.tags.add(*site_question.tags.all())

        # copy choices
        for sq_choice in SiteQuestionChoice.objects.filter(site_question=site_question).order_by('ordering'):
            SiteQuestionArchiveChoice.objects.create(
                ordering=sq_choice.ordering,
                choice=sq_choice.choice,
                site_question=archived_site_question
            )

        # remove the site question
        site_question.delete()

    latest_content = json.loads(latest_version.contents)
    with transaction.atomic():
        # initial form and section
        current_form = None
        current_section = None
        previous_section = None

        cnt = 0
        for row in latest_content:
            # convert row to a dict
            row_dict = convert_list_to_dict(row, current_form, current_section)

            # set current form and section
            current_form = row_dict.get('form')
            current_section = row_dict.get('section')

            # get the root question
            [root, is_default] = find_root_question(site, row_dict)

            # create the Site Question
            previous_section = create_site_question(site, root, row_dict, cnt, previous_section, is_default, None)

            cnt += 1

    # fetch all condition objects
    all_conditions = [Condition.objects.get(**item) for item in json.loads(latest_version.actions)]

    # update all site questions with the specified conditions
    for site_question in SiteQuestion.objects.filter(site=site):
        site_question.question.conditions.add(*all_conditions)

    # update the latest version finished date
    latest_version.updated_da_on = archived_at
    latest_version.save()

    return JsonResponse({'status': 'ok'}, safe=True)


@api_view(['GET'])
def request_removal(request, review_id):
    review = Review.objects.get(id=review_id)
    send_review_removal_email(request.user, review)

    return JsonResponse({'status': 'ok'}, safe=True)
