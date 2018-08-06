from django.db import models
from django.contrib.auth.models import User


class Review(models.Model):
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    location = models.TextField()
    started_at = models.DateTimeField()
    status = models.CharField(max_length=25)
    completed_at = models.DateTimeField(null=True)
    updated_da_summary = models.TextField(null=True)

    class Meta:
        db_table = 'review_review'


class ReviewRole(models.Model):
    user = models.ForeignKey(User, related_name='review_role', on_delete=models.CASCADE)
    role = models.CharField(max_length=25)

    class Meta:
        db_table = 'review_review_role'


class ReviewVersion(models.Model):
    review = models.ForeignKey(Review, related_name='versions', on_delete=models.CASCADE)
    revision = models.IntegerField(default=1, db_index=True)
    contents = models.TextField()
    summary = models.TextField(null=True)
    actions = models.TextField(null=True)
    info = models.TextField(null=True)
    is_locked = models.BooleanField(default=False)
    updated_da_on = models.DateTimeField(null=True)

    class Meta:
        db_table = 'review_review_version'
