from rest_framework import viewsets
from django.contrib.auth.models import User
from .models import Question, SiteQuestion, SavedCde, Source, Site, Form, Condition, ConditionCategory, Definition, SiteQuestionChoice, Choice, QuestionDefinition, UserLog, Tag, TagLabel
from .serializers import UserSerializer, SourceSerializer, SiteSerializer, FormSerializer, ConditionSerializer, ConditionCategorySerializer, QuestionSerializer, DefinitionSerializer, SiteQuestionSerializer, SavedCdeSerializer, ChoiceSerializer, SiteQuestionChoiceSerializer, TagSerializer, TagLabelSerializer
import hashlib
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework_json_api.pagination import PageNumberPagination
from django_filters import rest_framework as filters
from rest_framework import filters as drf_filters
import django_filters
from django.db.models import Q
import json
from django.shortcuts import render
from django.conf import settings
from .utils.helpers import parse_branching_logic
from itertools import chain
from .utils.helpers import download_redcap, parse_data_from_site_question
from django.db.models import Count
from django.utils import timezone


FORM_EXCLUDES = (
    # 'Consultations',
    # 'Demographics',
    # 'Dialysis',
    # 'Enzymemutation Analysis',
    # 'Followup Medical History',
    # 'Initial Medical History',
    # 'Labs',
    # 'Medications',
    # 'Physical Exam',
    # 'Pregnancy',
    # 'Radiologyimaging',
)

QUESTION_EXCLUDES = (
    'ibemc_clinic',
    # 'u_protocol_id',
)

CONDITION_EXCLUDES = (
    # 'Critical congenital heart disease (CCHD)',
    # 'Cystic fibrosis (CF)',
    # 'Fabry',
    # 'Hearing loss (HEAR)',
    # 'Niemann Pick Types A and B',
    # 'Primary congenital hypothyroidism (CH)',
    # 'Severe combined immunodeficiences (SCID)',
    # 'T-cell related lymphocyte deficiences',
)

CONDITION_CATEGORY_EXCLUDES = (
    # 'Condition not listed',
)

# SITE_EXCLUDES = (
#     'Mount Sinai',
# )

base_site_questions = SiteQuestion.objects.filter(
    ~Q(type='descriptive'),
    # ~Q(form__name__in=FORM_EXCLUDES),
    # ~Q(site__name__in=SITE_EXCLUDES),
    ~Q(name__in=QUESTION_EXCLUDES),
    # ~Q(question__conditions__name__in=CONDITION_EXCLUDES),
    # ~Q(question__conditions__category__name__in=CONDITION_CATEGORY_EXCLUDES),
    site__is_live=True
).order_by('ordering').annotate(dcount=Count('name'))


class SearchPaginationSet(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


def build_filters(request):
    # Initial query
    questions = base_site_questions

    # Handle the form filter
    if(request.GET['form']):
        # print('FORM: {}'.format(request.GET['form']))
        questions = questions.filter(form__name=request.GET['form'])

    # Handle the section filter
    if(request.GET['section']):
        # print('SECTION: {}'.format(request.GET['section']))
        questions = questions.filter(form__id=request.GET['section'])

    # Handle the condition category filter
    if(request.GET['conditionCategory']):
        questions = questions.filter(
            question__conditions__category__name=request.GET[
                'conditionCategory'
            ]
        )

    # Handle the condition filter
    if(request.GET['condition']):
        # print('CONDITION: {}'.format(request.GET['condition']))
        questions = questions.filter(
            question__conditions__name=request.GET['condition'])

    # Handle the keyword filter
    if(request.GET['keyword']):
        if(request.GET['keywordWholeWord'] == 'false'):
            # print('KEYWORD: {}'.format(request.GET['keyword']))
            questions = questions.filter(
                Q(name__icontains=request.GET['keyword']) |
                Q(question__definitions__definition__icontains=request.GET['keyword']) |
                Q(question__definitions__note__icontains=request.GET['keyword']) |
                Q(text__icontains=request.GET['keyword']) |
                Q(type__icontains=request.GET['keyword'])
            )
        else:
            # print('KEYWORD: {}'.format(request.GET['keyword']))
            regex = '[[:<:]]' + request.GET['keyword'] + '[[:>:]]'
            questions = questions.filter(
                Q(name__iregex=regex) |
                Q(question__definitions__definition__iregex=regex) |
                Q(question__definitions__note__iregex=regex) |
                Q(text__iregex=regex) |
                Q(type__iregex=regex)
            )

    # Handle site filter
    if(request.GET['site']):
        # print('SITE: {}'.format(request.GET['site']))
        questions = questions.filter(site__name=request.GET['site'])
    else:
        questions = questions.filter(
            tags__label='LpdrDefault', tags__value=True
        )

    return questions


@api_view(['POST'])
def auth_view(request):
    if (type(request.user).__name__ == 'AnonymousUser'):
        return JsonResponse({'errors': [
            {'detail': 'Invalid headers, please set headers to login'}
        ]}, status=401)

    if request.user.id:
        token = hashlib.md5(request.user.username.encode('utf-8'))
        return JsonResponse({
            'token': token.hexdigest(),
            'user_id': request.user.id
        })

    return JsonResponse({}, status=401)


@api_view(['GET'])
def add_all_cdes(request):
    saved_cde = SavedCde.objects.get(user_id=request.user.id)
    saved_cde_questions = json.loads(saved_cde.questions)

    site_question_ids = build_filters(request).values_list('id', flat=True)
    site_questions = SiteQuestion.objects.filter(
        id__in=site_question_ids
    ).order_by(
        'ordering'
    ).prefetch_related(
        'form'
    )

    for site_question in site_questions:
        foundForm = False
        foundSection = False

        # check if form exists
        for formId, form in enumerate(saved_cde_questions, start=0):
            if form.get('name') == site_question.form.name:
                foundForm = True
                # look for section
                for sectionId, section in enumerate(form.get(
                    'sections'
                ), start=0):
                    if section.get('name') == site_question.form.section:
                        foundSection = True
                        saved_cde_questions[formId].get(
                            'sections'
                        )[sectionId].get(
                            'cdes'
                        ).append(site_question.name)

                if not foundSection:
                    # create section/cde
                    section = {'name': site_question.form.section,
                               'cdes': [], 'expanded': False}
                    section.get('cdes').append(site_question.name)
                    saved_cde_questions[formId].get('sections').append(section)

        if not foundForm:
            # create form/section/cde
            form = {'name': site_question.form.name,
                    'sections': [], 'expanded': False}
            section = {'name': site_question.form.section,
                       'cdes': [], 'expanded': False}
            section.get('cdes').append(site_question.name)
            form.get('sections').append(section)

            saved_cde_questions.append(form)

    # save the data
    saved_cde.questions = json.dumps(saved_cde_questions)
    saved_cde.save()

    return JsonResponse({})


@api_view(['GET'])
def question_count(request):
    questions = build_filters(request)

    return JsonResponse({'count': len(questions)})


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class SourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Source.objects.all()
    serializer_class = SourceSerializer


class SiteViewSet(viewsets.ModelViewSet):
    queryset = Site.objects.filter(is_live=True).order_by('name')
    serializer_class = SiteSerializer
    filter_fields = ('name',)


class FormViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Form.objects.filter(
        ~Q(name__in=FORM_EXCLUDES),
        ~Q(questions=None)
    ).order_by('name', 'section')
    serializer_class = FormSerializer
    filter_fields = ('name',)


class ConditionFilter(filters.FilterSet):
    category = django_filters.CharFilter(name="category__name")
    search = django_filters.CharFilter(name="name", lookup_expr="icontains")

    class Meta:
        model = Condition
        fields = ('category', 'search',)


class ConditionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Condition.objects.filter(
        ~Q(name__in=CONDITION_EXCLUDES)).order_by('name')
    serializer_class = ConditionSerializer
    filter_class = ConditionFilter


class ConditionCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ConditionCategory.objects.filter(
        ~Q(name__in=CONDITION_CATEGORY_EXCLUDES)).order_by('label')
    serializer_class = ConditionCategorySerializer


class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Question.objects.filter(
        ~Q(name__in=QUESTION_EXCLUDES)).order_by('name')
    serializer_class = QuestionSerializer


class DefinitionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Definition.objects.all()
    serializer_class = DefinitionSerializer


class SiteQuestionFilter(drf_filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        return build_filters(request).prefetch_related(
            'form'
        ).prefetch_related(
            'choices'
        ).prefetch_related(
            'tags__label'
        ).prefetch_related(
            'question__definitions'
        )


class SiteQuestionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SiteQuestionSerializer
    pagination_class = SearchPaginationSet
    filter_backends = (SiteQuestionFilter, )

    def get_queryset(self):
        # log the query
        log = UserLog.objects.create(
            user=self.request.user,
            data=dict(self.request.GET),
            searched_at=timezone.now()
        )
        log.save()

        # make the actual query
        site_question_ids = base_site_questions.values_list('id', flat=True)
        return SiteQuestion.objects.filter(id__in=site_question_ids).order_by(
            'ordering'
        )


class SavedCdeViewSet(viewsets.ModelViewSet):
    queryset = SavedCde.objects.all()
    serializer_class = SavedCdeSerializer
    filter_fields = ('user__id',)


@api_view(['POST'])
def expand_all(request):
    # get the user and data
    user_id = request.POST.get('user_id')
    saved = SavedCde.objects.get(user_id=user_id)
    saved_cdes = json.loads(saved.questions)

    saved.questions = json.dumps(toggle_expanded(saved_cdes, True))
    saved.save()

    return JsonResponse({})


@api_view(['POST'])
def collapse_all(request):
    # get the user and data
    user_id = request.POST.get('user_id')
    saved = SavedCde.objects.get(user_id=user_id)
    saved_cdes = json.loads(saved.questions)

    saved.questions = json.dumps(toggle_expanded(saved_cdes, False))
    saved.save()

    return JsonResponse({})


def toggle_expanded(saved_cdes, value):
    for formId, form in enumerate(saved_cdes, start=0):
        saved_cdes[formId]['expanded'] = value
        for sectionId, section in enumerate(form.get('sections'), start=0):
            saved_cdes[formId].get('sections')[sectionId]['expanded'] = value

    return saved_cdes


def fetchSavedQuestionOrder(request):
    saved_cdes = json.loads(SavedCde.objects.get(
        user_id=request.user.id).questions)
    cdes = []

    for formId, form in enumerate(saved_cdes, start=0):
        for sectionId, section in enumerate(form.get('sections'), start=0):
            for cde in section.get('cdes'):
                cdes.append(cde)

    questions = base_site_questions.filter(name__in=cdes).prefetch_related(
        'form'
    ).prefetch_related(
        'site_choices__choice'
    ).prefetch_related(
        'choices'
    ).prefetch_related(
        'tags__label'
    ).prefetch_related(
        'question__definitions'
    )

    # add in more cdes if include all branching logic questions is checked
    questions_to_add = []
    if request.GET.get('branching'):
        for (site, logic) in questions.values_list('site_id', 'branching_logic'):
            if logic:
                add_questions = parse_branching_logic(site, logic)
                for add_question in add_questions:
                    ques = add_question.get('question')
                    if ques not in questions_to_add and ques not in questions:
                        cdes.append(ques.name)
                        questions_to_add.append(ques)

        # combine the added questions
        questions = list(chain(questions, questions_to_add))

    questions = dict([(obj.name, obj) for obj in questions])

    return [questions[name] for name in cdes]


@api_view(['GET'])
def summary(request):
    sorted_questions = fetchSavedQuestionOrder(request)
    previous_section = None

    all_questions = list(map(lambda item: parse_data_from_site_question(
        item, previous_section, False
    ), sorted_questions))

    url = '{}/view/LPDR/'.format(settings.APP_URL)

    return render(request, 'summary.html', {
        'questions': all_questions,
        'count': len(all_questions),
        'url': url
    })


@api_view(['GET'])
def redcap(request):
    data = fetchSavedQuestionOrder(request)

    return download_redcap('REDCap', data)


class ChoiceViewSet(viewsets.ModelViewSet):
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer


class SiteQuestionChoiceViewSet(viewsets.ModelViewSet):
    queryset = SiteQuestionChoice.objects.all()
    serializer_class = SiteQuestionChoiceSerializer


@api_view(['GET'])
def question_detail(request):
    results = {
        'data': {
            'type': 'question-detail',
            'id': None,
            'attributes': {}
        }
    }

    # get the site question
    site_question = SiteQuestion.objects.filter(
        question__name=request.GET.get('name'),
        tags__label__label='LpdrDefault',
        tags__value=True
    ).first()

    if not site_question:
        return JsonResponse({}, status=400, safe=False)

    source_number = 1

    results['data']['id'] = site_question.id
    fields = [
        'name',
        'text',
        'type',
        'min_val',
        'max_val',
        'unknown_val',
        'branching_logic'
    ]
    for field in fields:
        results['data']['attributes'][field.replace(
            '_', '-')] = getattr(site_question, field)

    results['data']['attributes']['site'] = site_question.site.display
    results['data']['attributes']['question'] = site_question.question.name
    results['data']['attributes']['form'] = site_question.form.name
    results['data']['attributes']['section'] = site_question.form.section

    definition = site_question.question.definitions.first()
    definition_data = {
        'definition': definition.definition if definition else None,
        'version': site_question.question.definitions.count(),
        'note': definition.note if definition else None,
        'source_name': definition.source.name if definition and definition.source else None,
        'source_address': definition.source.address if definition and definition.source else None,
        'source_number': source_number if definition and definition.source else None
    }

    if definition and definition.source:
        source_number += 1

    results['data']['attributes']['definition'] = json.dumps(definition_data)

    definitions = []
    for question_definition in QuestionDefinition.objects.filter(
        question=site_question.question
    ).order_by('-version'):
        definitions.append({
            'definition': question_definition.definition.definition if question_definition.definition else None,
            'note': question_definition.definition.note if question_definition.definition else None,
            'version': question_definition.version
        })

    results['data']['attributes']['all-definitions'] = json.dumps(definitions)

    tags = []
    for tag in site_question.tags.all():
        tags.append({
            'label': tag.label.label,
            'description': tag.label.description,
            'value': tag.value
        })
    results['data']['attributes']['tags'] = json.dumps(tags)

    choices = []
    code_type = None
    for sq_choice in SiteQuestionChoice.objects.filter(
        site_question=site_question
    ).order_by('ordering'):
        definition = sq_choice.choice.definitions.first()

        codes = []
        for code in sq_choice.choice.codes.all():
            codes.append({
                'name': code.code_type.name,
                'description': code.code_type.description,
                'base_url': code.code_type.base_url,
                'type_note': code.code_type.note,
                'value': code.value,
                'note': code.note
            })

            code_type = code.code_type.name

        choices.append({
            'text': sq_choice.choice.text,
            'value': sq_choice.choice.value,
            'definition': definition.definition if definition else None,
            'note': definition.note if definition else None,
            'source_name': definition.source.name if definition and definition.source else None,
            'source_address': definition.source.address if definition and definition.source else None,
            'source_number': source_number if definition and definition.source else None,
            'codes': codes
        })

        if definition and definition.source:
            source_number += 1

    results['data']['attributes']['choices'] = json.dumps(choices)

    codes = []
    for code in site_question.question.codes.all():
        codes.append({
            'name': code.code_type.name,
            'description': code.code_type.description,
            'base_url': code.code_type.base_url,
            'type_note': code.code_type.note,
            'value': code.value,
            'note': code.note
        })

        if code.code_type:
            code_type = code.code_type.name

    results['data']['attributes']['code-type'] = code_type
    results['data']['attributes']['question-codes'] = json.dumps(codes)

    # parse branching logic
    branching_logic = []
    if results['data']['attributes']['branching-logic']:
        for logic in parse_branching_logic(site_question.site.id, results['data']['attributes']['branching-logic']):
            site_question = logic.get('question')
            logic_choices = []
            for sq_choice in SiteQuestionChoice.objects.filter(
                site_question=site_question
            ).order_by('ordering'):
                logic_choices.append({
                    'text': sq_choice.choice.text,
                    'value': sq_choice.choice.value,
                    # 'sorting': sq_choice.ordering,
                    'highlight': True if str(sq_choice.ordering) in logic.get('answer') else False
                })

            branching_logic.append({
                'text': site_question.text,
                'name': site_question.name,
                'choices': logic_choices,
                # 'answer': logic.get('answer')
            })

    results['data']['attributes'][
        'branching-questions'] = json.dumps(branching_logic)

    return JsonResponse(results, safe=False)


@api_view(['GET'])
def question_typeahead(request):
    is_default_label = TagLabel.objects.filter(label='LpdrDefault').first()

    try:
        term = request.GET['term']
        questions = SiteQuestion.objects.filter(Q(site__is_live=True) & Q(
            tags__label=is_default_label) & Q(name__contains=term))
        results = []

        for question in questions:
            results.append({
                'name': question.name,
                'text': question.text,
                'site': question.site.name
            })

            # exit after 15 results
            if len(results) == 15:
                break

        return JsonResponse(results, safe=False)
    except:
        return JsonResponse({'errors': [
            {'title': 'Page not found', 'code': 404}
        ]}, safe=False, status=404)


class TagLabelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TagLabel.objects.all()
    serializer_class = TagLabelSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


@api_view(['GET'])
def search_settings(request):
    api_settings = {
        'help_email_text': settings.HELP.get('EMAIL_TEXT'),
        'help_email': settings.HELP.get('EMAIL'),
        'help_email_subject': settings.HELP.get('EMAIL_SUBJECT'),
        'data_load_date': settings.DATA_LOAD_DATE,
    }

    # convert to JSON API
    results = {
        'data': {
            'id': 1,
            'type': 'settings',
            'attributes': api_settings
        }
    }

    return JsonResponse(results, safe=False)
