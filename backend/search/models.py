from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User


class Source(models.Model):
    name = models.CharField("Source Name", max_length=128)
    address = models.TextField("Source Site Address", null=True, blank=True)

    class Meta:
        db_table = 'search_sources'

    def __str__(self):
        return "{}: {}".format(self.name, self.address)


class Definition(models.Model):
    definition = models.TextField("Semantic Definition")
    note = models.TextField("Definition Note", null=True, blank=True)
    source = models.ForeignKey(Source, blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        db_table = 'search_definitions'

    def __str__(self):
        return self.definition


class ConditionCategory(models.Model):
    label = models.CharField("Label", max_length=255)
    name = models.CharField("Name", max_length=255, unique=True)
    ordering = models.IntegerField("Ordering")

    class Meta:
        db_table = 'search_condition_categories'


class Condition(models.Model):
    category = models.ForeignKey(ConditionCategory, related_name="conditions", on_delete=models.CASCADE)
    label = models.CharField("Label", max_length=255)
    name = models.CharField("Name", max_length=255)
    ordering = models.IntegerField("Ordering")

    class Meta:
        db_table = 'search_conditions'


class CodeType(models.Model):
    source = models.ForeignKey(Source, blank=True, null=True, on_delete=models.CASCADE)
    name = models.CharField("Name", max_length=100)
    description = models.TextField("Description")
    base_url = models.TextField("Base URL", blank=True, null=True)
    note = models.TextField("Note", blank=True, null=True)

    class Meta:
        db_table = 'search_code_types'


class Code(models.Model):
    code_type = models.ForeignKey(CodeType, on_delete=models.CASCADE)
    value = models.CharField("Value", max_length=255)
    note = models.TextField("Note", blank=True, null=True)

    class Meta:
        db_table = 'search_codes'


class Choice(models.Model):
    text = models.TextField("Choice Text")
    value = models.TextField("Choice Value")
    definitions = models.ManyToManyField(
        Definition, through='ChoiceDefinition')
    codes = models.ManyToManyField(Code)

    class Meta:
        db_table = 'search_choices'

    def __str__(self):
        return self.value


class Question(models.Model):
    name = models.CharField(
        "Question Name", max_length=100, unique=True, db_index=True)

    conditions = models.ManyToManyField(Condition, related_name="questions")
    definitions = models.ManyToManyField(
        Definition, through='QuestionDefinition', related_name="questions")
    codes = models.ManyToManyField(Code, related_name="questions")

    class Meta:
        db_table = 'search_questions'

    def __str__(self):
        return self.name


class Site(models.Model):
    name = models.CharField("Site Name", max_length=50)
    display = models.CharField("Site Display Name", max_length=150)
    pi = models.CharField("Site PI", max_length=255)
    is_live = models.BooleanField("Site Live?", default=True)

    class Meta:
        db_table = 'search_sites'

    def __str__(self):
        return "{} ({})".format(self.display, self.name)


class Form(models.Model):
    name = models.CharField("Form name", max_length=255, db_index=True)
    section = models.TextField("Section Name", null=True, blank=True)

    class Meta:
        db_table = 'search_forms'

    def __str__(self):
        return "{} > {}".format(self.name, self.section)


class TagLabel(models.Model):
    TAG_TYPES = (
        ('number', 'number'),
        ('text', 'text'),
        ('date', 'date'),
        ('boolean', 'boolean'),
    )

    label = models.CharField("Label", max_length=255, unique=True)
    type = models.CharField("Tag Type", max_length=50, choices=TAG_TYPES)
    description = models.TextField()

    class Meta:
        db_table = 'search_tag_labels'


class Tag(models.Model):
    label = models.ForeignKey(TagLabel, to_field='label', on_delete=models.CASCADE)
    value = models.TextField()

    class Meta:
        db_table = 'search_tags'


class SiteQuestion(models.Model):
    TYPE_CHOICES = (
        ('integer', 'Integer'),
        ('text', 'Text'),
        ('checkbox', 'Checkbox'),
        ('yesno', 'Yes/No'),
        ('dropdown', 'Dropdown'),
        ('date_mdy', 'Date: MM/DD/YYYY'),
        ('date_dmy', 'Date: DD/MM/YYYY'),
        ('date_ymd', 'Date: YYYYY/MM/DD'),
        ('datetime_mdy', 'Datetime: MM/DD/YYYY HH:MM'),
        ('datetime_dmy', 'Datetime: DD/MM/YYYY HH:MM'),
        ('datetime_ymd', 'Datetime: YYYY/MM/DD HH:MM'),
        ('datetime_seconds_mdy',
            'Datetime with seconds: MM/DD/YYYY HH:MM:SS'),
        ('datetime_seconds_dmy',
            'Datetime with seconds: DD/MM/YYYY HH:MM:SS'),
        ('datetime_seconds_ymd',
            'Datetime with seconds: YYYY/MM/DD HH:MM:SS'),
        ('email', 'Email'),
        ('alpha_only', 'Letters Only'),
        ('mrn_10d', 'MRN (10 digits)'),
        ('number', 'Number'),
        ('number_1dp', 'Number with 1 Decimal Place'),
        ('number_2dp', 'Number with 2 Decimal Place'),
        ('number_3dp', 'Number with 3 Decimal Place'),
        ('number_4dp', 'Number with 4 Decimal Place'),
        ('phone_australia', 'Phone - Australia'),
        ('phone', 'Phone'),
        ('postalcode_australia', 'Postal Code - Australia'),
        ('postalcode_canada', 'Postal Code - Canada'),
        ('ssn', 'Social Security Number - U.S.'),
        ('time', 'Time: HH:MM'),
        ('time_mm_ss', 'Time: MM:SS'),
        ('vmrn', 'Vanderbilt MRN'),
        ('zipcode', 'Zipcode - U.S.'),
        ('truefalse', 'True/False'),
        ('notes', 'Note'),
        ('description', 'Descipriton'),
        ('sql', 'SQL Field'),
        ('radio', 'Radio Button'),
        ('calc', 'Calculated Field'),
        ('matrix', 'Matrix'),
        ('descriptive', 'Descriptive'),
    )

    site = models.ForeignKey(Site, related_name="questions", on_delete=models.CASCADE)
    form = models.ForeignKey(Form, related_name="questions", on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name="site_questions", on_delete=models.CASCADE)
    # is_default = models.BooleanField("Is default?", default=False)
    name = models.CharField("Name", max_length=100, db_index=True)
    text = models.TextField("Text", null=True, db_index=True)
    type = models.CharField("Type", max_length=24, choices=TYPE_CHOICES, null=True, db_index=True)
    note = models.TextField("Note", null=True, blank=True)
    calculation = models.TextField("Calculation", blank=True, null=True, help_text="If this field is a result of a calculation, enter it here")
    min_val = models.FloatField("Minimun Value", null=True, blank=True, help_text="The minimum value a user can enter for this field, if applicable.")
    max_val = models.FloatField("Maximum Value", null=True, blank=True, help_text="The maximum value a user can enter for this field, if applicable.")
    validation = models.TextField("Validation", blank=True, null=True, help_text="Text validation entered here")
    ordering = models.IntegerField("Ordering", null=True)
    align = models.CharField("Alignment", max_length=255, blank=True, null=True)
    matrix_name = models.CharField("Matrix Name", max_length=255, blank=True, null=True)
    unknown_val = models.CharField("Unknown Value", max_length=255, blank=True, null=True)
    branching_logic = models.TextField("Branching Logic", blank=True, null=True)
    # status = models.CharField("Status", max_length=50, blank=True, null=True)
    # is_identifier = models.BooleanField("Is an identifier?", default=False)
    # is_required = models.BooleanField("Is required?", default=False)

    choices = models.ManyToManyField(Choice, through='SiteQuestionChoice')
    tags = models.ManyToManyField(Tag)

    class Meta:
        db_table = 'search_site_questions'

    def __str__(self):
        return "{}: {}".format(self.name, self.text)


class SiteQuestionChoice(models.Model):
    site_question = models.ForeignKey(SiteQuestion, related_name='site_choices', on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    ordering = models.IntegerField("Ordering")

    class Meta:
        ordering = ('ordering',)
        db_table = 'search_site_question_choices'


class QuestionDefinition(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    definition = models.ForeignKey(Definition, on_delete=models.CASCADE)
    version = models.IntegerField("Version")

    class Meta:
        db_table = 'search_question_definitions'


class ChoiceDefinition(models.Model):
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    definition = models.ForeignKey(Definition, on_delete=models.CASCADE)
    version = models.IntegerField("Version")

    class Meta:
        db_table = 'search_choice_definitions'


class SavedCde(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    questions = JSONField()

    class Meta:
        db_table = 'search_saved_cdes'

    def __str__(self):
        return 'SavedCdes for {}'.format(self.user.username)


class UserLog(models.Model):
    user = models.ForeignKey(User, related_name="search_logs", on_delete=models.CASCADE)
    data = models.TextField()
    searched_at = models.DateTimeField()

    class Meta:
        db_table = 'search_user_logs'


class SiteQuestionArchive(models.Model):
    TYPE_CHOICES = (
        ('integer', 'Integer'),
        ('text', 'Text'),
        ('checkbox', 'Checkbox'),
        ('yesno', 'Yes/No'),
        ('dropdown', 'Dropdown'),
        ('date_mdy', 'Date: MM/DD/YYYY'),
        ('date_dmy', 'Date: DD/MM/YYYY'),
        ('date_ymd', 'Date: YYYYY/MM/DD'),
        ('datetime_mdy', 'Datetime: MM/DD/YYYY HH:MM'),
        ('datetime_dmy', 'Datetime: DD/MM/YYYY HH:MM'),
        ('datetime_ymd', 'Datetime: YYYY/MM/DD HH:MM'),
        ('datetime_seconds_mdy',
            'Datetime with seconds: MM/DD/YYYY HH:MM:SS'),
        ('datetime_seconds_dmy',
            'Datetime with seconds: DD/MM/YYYY HH:MM:SS'),
        ('datetime_seconds_ymd',
            'Datetime with seconds: YYYY/MM/DD HH:MM:SS'),
        ('email', 'Email'),
        ('alpha_only', 'Letters Only'),
        ('mrn_10d', 'MRN (10 digits)'),
        ('number', 'Number'),
        ('number_1dp', 'Number with 1 Decimal Place'),
        ('number_2dp', 'Number with 2 Decimal Place'),
        ('number_3dp', 'Number with 3 Decimal Place'),
        ('number_4dp', 'Number with 4 Decimal Place'),
        ('phone_australia', 'Phone - Australia'),
        ('phone', 'Phone'),
        ('postalcode_australia', 'Postal Code - Australia'),
        ('postalcode_canada', 'Postal Code - Canada'),
        ('ssn', 'Social Security Number - U.S.'),
        ('time', 'Time: HH:MM'),
        ('time_mm_ss', 'Time: MM:SS'),
        ('vmrn', 'Vanderbilt MRN'),
        ('zipcode', 'Zipcode - U.S.'),
        ('truefalse', 'True/False'),
        ('notes', 'Note'),
        ('description', 'Descipriton'),
        ('sql', 'SQL Field'),
        ('radio', 'Radio Button'),
        ('calc', 'Calculated Field'),
        ('matrix', 'Matrix'),
        ('descriptive', 'Descriptive'),
    )

    site = models.ForeignKey(Site, related_name="questions_archive", on_delete=models.CASCADE)
    form = models.ForeignKey(Form, related_name="questions_archive", on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name="site_questions_archive", on_delete=models.CASCADE)
    # is_default = models.BooleanField("Is default?", default=False)
    name = models.CharField("Name", max_length=100, db_index=True)
    text = models.TextField("Text", null=True, db_index=True)
    type = models.CharField("Type", max_length=24, choices=TYPE_CHOICES, null=True, db_index=True)
    note = models.TextField("Note", null=True, blank=True)
    calculation = models.TextField("Calculation", blank=True, null=True, help_text="If this field is a result of a calculation, enter it here")
    min_val = models.FloatField("Minimun Value", null=True, blank=True, help_text="The minimum value a user can enter for this field, if applicable.")
    max_val = models.FloatField("Maximum Value", null=True, blank=True, help_text="The maximum value a user can enter for this field, if applicable.")
    validation = models.TextField("Validation", blank=True, null=True, help_text="Text validation entered here")
    ordering = models.IntegerField("Ordering", null=True)
    align = models.CharField("Alignment", max_length=255, blank=True, null=True)
    matrix_name = models.CharField("Matrix Name", max_length=255, blank=True, null=True)
    unknown_val = models.CharField("Unknown Value", max_length=255, blank=True, null=True)
    branching_logic = models.TextField("Branching Logic", blank=True, null=True)
    # status = models.CharField("Status", max_length=50, blank=True, null=True)
    # is_identifier = models.BooleanField("Is an identifier?", default=False)
    # is_required = models.BooleanField("Is required?", default=False)

    choices = models.ManyToManyField(Choice, through='SiteQuestionArchiveChoice')
    tags = models.ManyToManyField(Tag)
    date_archived = models.DateTimeField()

    class Meta:
        db_table = 'search_site_questions_archive'

    def __str__(self):
        return "{}: {}".format(self.name, self.text)


class SiteQuestionArchiveChoice(models.Model):
    site_question = models.ForeignKey(SiteQuestionArchive, related_name='site_choices', on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    ordering = models.IntegerField("Ordering")

    class Meta:
        ordering = ('ordering',)
        db_table = 'search_site_question_archive_choices'
