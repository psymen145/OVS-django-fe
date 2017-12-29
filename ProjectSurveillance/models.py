from __future__ import unicode_literals
from django.contrib.auth.models import User

from django.db import models

class Accesspath(models.Model):
    accessid = models.AutoField(db_column='ID', primary_key=True)
    pathlink = models.CharField(db_column='PathLink', max_length=2000, null=True)
    name = models.CharField(db_column='Name', max_length=1000, null=True)
    archive = models.NullBooleanField(db_column='Archive')

    class Meta:
        db_table = 'VS_AccessPath'

class Dataset(models.Model):
    datasetid = models.AutoField(db_column='DataSetID', primary_key=True)
    setname = models.CharField(db_column='SetName', max_length=255)
    setdesc = models.CharField(db_column='SetDesc', max_length=500, null=True)
    rules = models.CharField(db_column='Rules', max_length=255, null=True)
    review = models.NullBooleanField(db_column='Review')

    def __str__(self):
        return self.setname
    
    class Meta:
        db_table = 'VS_Dataset'


class DetailType(models.Model):
    detailtypeid = models.AutoField(db_column='DetailTypeID', primary_key=True)
    detaildesc = models.CharField(db_column='DetailDesc', max_length=500)
    datasetid = models.ForeignKey('Dataset', on_delete=models.CASCADE, db_column='datasetid', blank=True, null=True)
    drive = models.NullBooleanField(db_column='Drive')
    archive = models.NullBooleanField(db_column='Archive')

    def __str__(self):
        return self.detaildesc

    class Meta:
        db_table = 'VS_Detail_Type'


class OrganizationType(models.Model):
    orgtypeid = models.AutoField(db_column='OrgTypeID', primary_key=True)
    typename = models.CharField(db_column='TypeName', max_length=255)

    def __str__(self):
        return self.typename

    class Meta:
        db_table = 'VS_Organization_Type'


class Organization(models.Model):
    orgid = models.AutoField(db_column='OrgID', primary_key=True)
    orgname = models.CharField(db_column='OrgName', max_length=255)
    description = models.CharField(db_column='Description', max_length=500, null=True)
    street = models.CharField(db_column='Street', max_length=255, null=True)
    city = models.CharField(db_column='City', max_length=50)
    state = models.CharField(db_column='State', max_length=50)
    zipcode = models.CharField(db_column='Zipcode', max_length=25, null=True)
    orgtypeid = models.ForeignKey('OrganizationType', models.SET_NULL, db_column='OrgTypeID', blank=True, null=True)
    orgqueue = models.NullBooleanField(db_column='OrgQueue')
    inactive = models.NullBooleanField(db_column='Inactive')
    
    def __str__(self):
        return self.orgname

    class Meta:
        db_table = 'VS_Organization'


class Project(models.Model):
    projectid = models.AutoField(db_column='ProjectID', primary_key=True)
    phaseid = models.ForeignKey('WorkPhase', models.CASCADE, db_column='PhaseID', null=True)
    projname = models.CharField(db_column='ProjName', max_length=255)
    alternateid = models.CharField(db_column='AlternateID', max_length=255, null=True)
    accesslinkid = models.IntegerField(db_column='AccessLinkID', blank=True, null=True)
    archive = models.NullBooleanField(db_column='Archive')
    '''
    int_ext_choices = (
        ('Internal', 'int'),
        ('External', 'ext'),
        ('Collaboration', 'collab'),
    )
    intext = models.CharField(max_length=50,db_column='IntExt',choices=int_ext_choices, null=True)
    '''

    def __str__(self):
        return self.projname

    class Meta:
        db_table = 'VS_Project'


class VSUser(models.Model):
    userid = models.AutoField(db_column="UserID", primary_key=True)
    fname = models.CharField(db_column='Fname', max_length=50)
    lname = models.CharField(db_column='Lname', max_length=50)
    useremail = models.EmailField(db_column='UserEmail')
    phone = models.CharField(db_column='Phone', max_length=25, null=True)

    def __str__(self):
        return "{0} {1}    <{2}>".format(self.fname,self.lname,self.useremail)

    class Meta:
        db_table = 'VS_User'


class Variable(models.Model):
    varid = models.AutoField(db_column='VarID', primary_key=True)
    varname = models.CharField(db_column='VarName', max_length=255, null=True)
    shortdesc = models.CharField(db_column='ShortDesc', max_length=255, null=True)
    fulldesc = models.CharField(db_column='FullDesc', max_length=500, null=True)

    def __str__(self):
        return self.varname

    class Meta:
        db_table = 'VS_Variable'


class VariableDataset(models.Model):
    vardatasetid = models.AutoField(db_column='VarDataSetID', primary_key=True)
    varid = models.ForeignKey('Variable', models.CASCADE, db_column='VarID', blank=True, null=True)
    datasetid = models.ForeignKey(Dataset, models.CASCADE, db_column='DataSetID', blank=True, null=True)
    archive = models.NullBooleanField(db_column='Archive')

    class Meta:
        db_table = 'VS_Variable_Dataset'
        

class ProjectVariable(models.Model):
    projvarid = models.AutoField(db_column='ProjVarID', primary_key=True)
    vardatasetid = models.ForeignKey('VariableDataset', models.CASCADE, db_column='VarDataSetID', blank=True, null=True)
    projectid = models.ForeignKey('Project', models.CASCADE, db_column='ProjectID')
    datelogged = models.DateField(db_column='DateLogged') 
    analysis = models.NullBooleanField(db_column='Analysis')
    joined = models.NullBooleanField(db_column='Joined')
    archive = models.NullBooleanField(db_column='Archive')

    class Meta:
        db_table = 'VS_Project_Variable'


class ProjectDatasetRequest(models.Model):
    projdatasetrequestid = models.AutoField(db_column='ProjDataSetRequestID', primary_key=True) 
    projectid = models.ForeignKey('Project', models.CASCADE, db_column='ProjectID', blank=True, null=True)
    datasetid = models.ForeignKey('Dataset', models.SET_NULL, db_column='DataSetID', blank=True, null=True)
    datelogged = models.DateField(db_column='DateLogged')
    archive = models.NullBooleanField(db_column='Archive')

    class Meta:
        db_table = 'VS_Project_Dataset_Request'


class ProjectDetail(models.Model):
    detailid = models.AutoField(db_column='DetailID', primary_key=True) 
    userid = models.ForeignKey('VSUser', models.CASCADE, db_column='UserID', null=True)
    projectid = models.ForeignKey('Project', models.CASCADE, db_column='ProjectID', null=True)
    detailtypeid = models.ForeignKey('DetailType', models.CASCADE, db_column='DetailTypeID', null=True)
    note = models.TextField(db_column='Note', null=True)
    dateofevent = models.DateField(db_column='DateOfEvent')
    
    class Meta:
        db_table = 'VS_Project_Detail'


class UserOrganization(models.Model):
    userorgid = models.AutoField(db_column='UserOrgID', primary_key=True)
    orgid = models.ForeignKey('Organization', models.CASCADE, db_column='OrgID', blank=True, null=True)
    userid = models.ForeignKey('VSUser', models.CASCADE, db_column='UserID', blank=True, null=True)
    archive = models.NullBooleanField(db_column='Archive')

    class Meta:
        db_table = 'VS_User_Organization'


class UserProject(models.Model):
    usersprojid = models.AutoField(db_column='UsersProjID', primary_key=True)
    userid = models.ForeignKey('VSUser', models.CASCADE, db_column='UserID') 
    projectid = models.ForeignKey('Project', models.CASCADE, db_column='ProjectID')
    projrole = models.CharField(db_column="ProjRole", max_length=255, null=True)
    begindate = models.DateField(db_column='BeginDate')
    enddate = models.DateField(db_column='EndDate', blank=True, null=True)
    archive = models.NullBooleanField(db_column='Archive')
    datatranscoordinator = models.NullBooleanField(db_column='DataTransCoordinator')

    class Meta:
        db_table = 'VS_User_Project'


class Component(models.Model):
    compid = models.AutoField(db_column='CompID', primary_key=True)
    projectid = models.ForeignKey(Project, models.CASCADE, db_column='ProjectID')
    comptype = models.CharField(db_column='CompType', max_length=255, null=True)
    compnote = models.TextField(db_column='CompNote', max_length=1000, null=True)
    compactive = models.DateField(db_column='CompActive')
    compexpire = models.DateField(db_column='CompExpire')
    archive = models.NullBooleanField(db_column='Archive')

    class Meta:
        db_table = 'VS_Component'

    def __str__(self):
        return comptype


class WorkPhase(models.Model):
    phaseid = models.AutoField(db_column='PhaseID', primary_key=True)
    phase = models.CharField(db_column='Phase', max_length=255)
    phaseorder = models.IntegerField(db_column='PhaseOrder', null=True)

    class Meta:
        db_table = 'VS_Work_Phase'


class WorkStep(models.Model):
    stepid = models.AutoField(db_column='StepID', primary_key = True)
    step = models.CharField(db_column='Step', max_length=2000, null=True)
    note = models.TextField(db_column='Note', max_length=4000, null=True)
    archive = models.NullBooleanField(db_column='Archive')

    class Meta:
        db_table = 'VS_Work_Step'


class ProjectActivity(models.Model):
    activityid = models.AutoField(db_column='ActivityID', primary_key=True)
    projectid = models.ForeignKey(Project, models.CASCADE, db_column='ProjectID')
    workstepid = models.ForeignKey(WorkStep, models.CASCADE, db_column='WorkstepID')
    actionneededby = models.IntegerField(db_column='ActionNeededBy', null=True)
    loggedby = models.ForeignKey(VSUser, models.CASCADE, db_column='LoggedBy')
    datelogged = models.DateField(db_column='DateLogged')
    note = models.TextField(db_column='Note', max_length=4000, null=True)
    archive = models.NullBooleanField(db_column='Archive')
    rowcreation = models.DateTimeField(db_column='RowCreation', auto_now_add=True)

    class Meta:
        db_table = 'VS_Project_Activity'
