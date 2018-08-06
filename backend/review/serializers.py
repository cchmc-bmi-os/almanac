from rest_framework import serializers
from .models import Review, ReviewVersion, ReviewRole
from django.contrib.auth.models import User
from rest_framework_json_api.relations import ResourceRelatedField
from .utils.email import send_review_version_email


class ReviewVersionSerializer(serializers.ModelSerializer):
    included_serializers = {
        'review': 'review.serializers.ReviewSerializer'
    }

    review = ResourceRelatedField(queryset=Review.objects)

    class Meta:
        model = ReviewVersion
        fields = '__all__'

    def create(self, validated_data):
        send_review_version_email(self.context['request'].user, validated_data)

        return ReviewVersion.objects.create(**validated_data)


class ReviewSerializer(serializers.ModelSerializer):
    included_serializers = {
        'user': 'search.serializers.UserSerializer',
        'versions': 'review.serializers.ReviewVersionSerializer'
    }

    user = ResourceRelatedField(queryset=User.objects)
    versions = ResourceRelatedField(read_only=True, many=True)

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('versions',)


class ReviewRoleSerializer(serializers.ModelSerializer):
    included_serializers = {
        'user': 'search.serializers.UserSerializer',
    }

    user = ResourceRelatedField(queryset=User.objects)

    class Meta:
        model = ReviewRole
        fields = '__all__'
