from django.conf import settings
from django.urls import include, path, re_path
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from search.views import *
from review.views import *

router = DefaultRouter(trailing_slash=False)
router.register('api/v1/conditions', ConditionViewSet)
router.register('api/v1/condition-categories', ConditionCategoryViewSet)
router.register('api/v1/forms', FormViewSet)
router.register('api/v1/questions', QuestionViewSet)
router.register('api/v1/saved-cdes', SavedCdeViewSet)
router.register('api/v1/sites', SiteViewSet)
router.register('api/v1/sources', SourceViewSet)
router.register('api/v1/site-questions', SiteQuestionViewSet, base_name='site_questions')
router.register('api/v1/users', UserViewSet)
router.register('api/v1/definitions', DefinitionViewSet)
router.register('api/v1/site-question-choices', SiteQuestionChoiceViewSet)
router.register('api/v1/choices', ChoiceViewSet)
router.register('api/v1/tag-labels', TagLabelViewSet)
router.register('api/v1/tags', TagViewSet)
router.register('api/v1/reviews', ReviewViewSet, 'reviews')
router.register('api/v1/review-versions', ReviewVersionViewSet, 'review-versions')
router.register('api/v1/review-roles', ReviewRoleViewSet, 'review-roles')


urlpatterns = [
    # path(r'^admin/', include(admin.site.urls)),
    path('api/v1/auth', auth_view),
    path('api/v1/questions/count', question_count),
    path('api/v1/questions/typeahead', question_typeahead),
    path('api/v1/saved-cdes/addall', add_all_cdes),
    path('api/v1/saved-cdes/expandall', expand_all),
    path('api/v1/saved-cdes/collapseall', collapse_all),
    path('api/v1/saved-cdes/summary', summary),
    path('api/v1/saved-cdes/redcap', redcap),
    path('api/v1/question-details', question_detail),
    path('api/v1/settings/1', search_settings),
    path('api/v1/reviews/upload', upload),
    path('api/v1/reviews/<int:review_id>/diff', diff),
    path('api/v1/reviews/<int:review_id>/final', final_calculation),
    path('api/v1/reviews/<int:review_id>/export', export_redcap),
    path('api/v1/reviews/<int:review_id>/update/<int:site_id>', update_da),
    path('api/v1/reviews/<int:review_id>/request-removal', request_removal),
    path('', include(router.urls)),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        re_path('^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
