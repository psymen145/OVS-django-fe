from django.db import models
from ProjectSurveillance.models import Project

class DatapullAuthor(models.Model):
    associatedid = models.IntegerField(db_column='AssociatedID', blank=True, null=True)  # Field name made lowercase.
    forename = models.CharField(db_column='ForeName', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    lastname = models.CharField(db_column='LastName', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    affiliation = models.TextField(db_column='Affiliation', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'DataPull_Author'


class DatapullDetail(models.Model):
    pullid = models.ForeignKey('DatapullId', models.CASCADE, db_column='PullID', blank=True, null=True)  # Field name made lowercase.
    associatedid = models.IntegerField(db_column='AssociatedID', blank=True, null=True)  # Field name made lowercase.
    valuestore = models.CharField(db_column='ValueStore', max_length=255, blank=True, null=True)  # Field name made lowercase.
    note = models.CharField(db_column='Note', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    projectid = models.ForeignKey(Project, models.CASCADE, db_column='ProjectID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'DataPull_Detail'


class DatapullId(models.Model):
    pullid = models.AutoField(db_column='PullID', primary_key=True)
    pulldate = models.DateField(db_column='PullDate', auto_now=True, blank=True, null=True)
    pullname = models.CharField(db_column='PullName', max_length=1000, blank=True, null=True)
    pullquery = models.TextField(db_column='PullQuery', blank=True, null=True)
    query_type = (
        ('Keyword(s)', 'keyword'),
        ('Author(s)', 'author'),
    )
    pulltype = models.CharField(db_column='PullType', max_length=255, choices=query_type, blank=True, null=True)
    source_choices = (
        ('Pubmed', 'PUBMED'),
    )
    pullsource = models.CharField(db_column='PullSource', max_length=255, choices=source_choices, blank=True, null=True)
    pullby = models.CharField(db_column='PullBy', max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'DataPull_ID'


class DatapullKeyword(models.Model):
    associatedid = models.IntegerField(db_column='AssociatedID', blank=True, null=True)  # Field name made lowercase.
    keywordvalue = models.CharField(db_column='KeywordValue', max_length=255, blank=True, null=True)  # Field name made lowercase.
    category1 = models.CharField(db_column='Category1', max_length=255, blank=True, null=True)  # Field name made lowercase.
    category2 = models.CharField(db_column='Category2', max_length=255, blank=True, null=True)  # Field name made lowercase.
    category3 = models.CharField(db_column='Category3', max_length=255, blank=True, null=True)  # Field name made lowercase.
    category4 = models.CharField(db_column='Category4', max_length=255, blank=True, null=True)  # Field name made lowercase.
    category5 = models.CharField(db_column='Category5', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'DataPull_Keyword'


class DatapullText(models.Model):
    associatedid = models.IntegerField(db_column='AssociatedID', blank=True, null=True)  # Field name made lowercase.
    nlmcategory = models.CharField(db_column='NLMCategory', max_length=255, blank=True, null=True)  # Field name made lowercase.
    label = models.CharField(db_column='Label', max_length=255, blank=True, null=True)  # Field name made lowercase.
    abstracttext = models.TextField(db_column='AbstractText', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'DataPull_Text'


class DatapullTitle(models.Model):
    associatedid = models.IntegerField(db_column='AssociatedID', blank=True, null=True)  # Field name made lowercase.
    title = models.CharField(db_column='Title', max_length=1000, blank=True, null=True)  # Field name made lowercase.
    journal = models.CharField(db_column='Journal', max_length=500, blank=True, null=True)  # Field name made lowercase.
    publicationdate = models.CharField(db_column='PublicationDate', max_length=10, blank=True, null=True)  # Field name made lowercase.
    optionalid01 = models.CharField(db_column='OptionalID01', max_length=500, blank=True, null=True)  # Field name made lowercase.
    optionalid02 = models.CharField(db_column='OptionalID02', max_length=500, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'DataPull_Title'
