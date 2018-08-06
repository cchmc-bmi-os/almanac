from rest_framework import serializers
from rest_framework_json_api.relations import ResourceRelatedField
from django.contrib.auth.models import User
from .models import Site, Form, Condition, ConditionCategory, SiteQuestion, Question, Definition, Source, SavedCde, SiteQuestionChoice, Choice, Tag, TagLabel


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        # fields = '__all__'
        exclude = ('password',)


class SiteSerializer(serializers.ModelSerializer):
    pi = serializers.CharField(allow_blank=True)

    class Meta:
        model = Site
        fields = '__all__'


class FormSerializer(serializers.ModelSerializer):

    class Meta:
        model = Form
        fields = '__all__'


class ConditionCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = ConditionCategory
        fields = '__all__'


class ConditionSerializer(serializers.ModelSerializer):
    included_serializers = {
        'category': 'search.serializers.ConditionCategorySerializer'
    }

    category = ResourceRelatedField(queryset=ConditionCategory.objects.all())

    class Meta:
        model = Condition
        fields = '__all__'


class SiteQuestionChoiceSerializer(serializers.ModelSerializer):
    included_serializers = {
        'site_question': 'search.serializers.SiteQuestionSerializer',
        'choice': 'search.serializers.ChoiceSerializer'
    }

    class Meta:
        model = SiteQuestionChoice
        fields = '__all__'
        read_only_fields = ('site_question', 'choice',)


class SourceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Source
        fields = '__all__'


class DefinitionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Definition
        fields = '__all__'


class ChoiceSerializer(serializers.ModelSerializer):
    included_serializers = {
        'definitions': 'search.serializers.DefinitionSerializer'
    }

    definitions = ResourceRelatedField(read_only=True, many=True)

    class Meta:
        fields = ('id', 'value', 'text', 'definitions')
        model = Choice
        read_only_fields = ('definitions',)


class SiteQuestionSerializer(serializers.ModelSerializer):
    included_serializers = {
        'tags': 'search.serializers.TagSerializer',
        'choices': 'search.serializers.ChoiceSerializer',
        'question': 'search.serializers.QuestionSerializer',
        'form': 'search.serializers.FormSerializer',
        'site': 'search.serializers.SiteSerializer'
    }

    tags = ResourceRelatedField(read_only=True, many=True)
    choices = ResourceRelatedField(read_only=True, many=True)
    question = ResourceRelatedField(read_only=True)
    form = ResourceRelatedField(read_only=True)
    site = ResourceRelatedField(read_only=True)

    class Meta:
        model = SiteQuestion
        fields = '__all__'
        read_only_fields = ('tags', 'choices', 'question', 'form', 'site',)


class QuestionSerializer(serializers.ModelSerializer):
    included_serializers = {
        'definitions': 'search.serializers.DefinitionSerializer'
    }

    definitions = ResourceRelatedField(read_only=True, many=True)

    class Meta:
        model = Question
        fields = '__all__'
        read_only_fields = ('definitions',)


class SavedCdeSerializer(serializers.ModelSerializer):
    included_serializers = {
        'user': 'search.serializers.UserSerializer'
    }

    user = ResourceRelatedField(read_only=True)

    class Meta:
        model = SavedCde
        fields = '__all__'
        read_only_fields = ('user',)


class TagSerializer(serializers.ModelSerializer):
    included_serializers = {
        'label': 'search.serializers.TagLabelSerializer',
    }

    label = ResourceRelatedField(read_only=True)

    class Meta:
        model = Tag
        fields = '__all__'


class TagLabelSerializer(serializers.ModelSerializer):

    class Meta:
        model = TagLabel
        fields = '__all__'
