from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.utils import timezone
from datetime import timedelta
from django.core.validators import RegexValidator

from .models import *

class UserForm(forms.Form):
        fname = forms.CharField(label="First Name", max_length=50, required=True)
        lname = forms.CharField(label="Last Name", max_length=50, required=True)
        useremail = forms.EmailField(label="Email", required=True)
        phone_regex = RegexValidator(regex=r"^\d{9,15}?$", message="Invalid format")
        phone = forms.CharField(label="Phone", validators=[phone_regex], max_length=15)
        orgname = forms.ModelChoiceField(label="Organization", queryset=Organization.objects.all().order_by("orgname"),
                                         empty_label="")

        def __init__(self, *args, **kwargs):
                super(UserForm, self).__init__(*args, **kwargs)
                for field_name, field in self.fields.items():
                    field.widget.attrs["class"] = "form-control"

        def clean_useremail(self):
                email = self.cleaned_data["useremail"]
                if VSUser.objects.filter(useremail = email).exists():
                        raise forms.ValidationError("Email already exists")
                return email

class ProjectForm(forms.Form):
        orgname = forms.ModelChoiceField(label="Organization", queryset=Organization.objects.all().order_by("orgname"),
                                         empty_label="")

        orgname2 = forms.ModelChoiceField(label="Co-Organization", queryset=Organization.objects.all().order_by("orgname"),
                                         empty_label="")
        project_name = forms.CharField(label="Project Name", max_length=255, required=True)
        TYPE_CHOICES = (
                ("",""),
                ('int', 'Internal'),
                ('ext', 'External'),
                ('collab', 'Collaboration'),
        )
        intext = forms.ChoiceField(label='Internal/External', widget=forms.Select(),
                                   choices = TYPE_CHOICES, required=True)
        startdate = forms.DateField(label='Start Date',
                                    widget=forms.SelectDateWidget(years = list(range(2013,2030))),
                                    required=True,
                                    initial=timezone.now())
        est_enddate = forms.DateField(label='Estimated End Date',
                                      widget=forms.SelectDateWidget(years = list(range(2013,2030))),
                                      required=False)

        attached_user = forms.ModelMultipleChoiceField(label='Associated user(s)', queryset=VSUser.objects.all().order_by('fname'))

        def __init__(self, *args, **kwargs):
                super(ProjectForm, self).__init__(*args, **kwargs)
                for field_name, field in self.fields.items():
                    field.widget.attrs["class"] = "form-control"

        def clean_project_name(self):
                project_name = self.cleaned_data["project_name"]
                if Project.objects.filter(projname = project_name).exists():
                        raise forms.ValidationError("Project name already exists")
                return project_name

        def clean_orgname2(self):
                if self.cleaned_data["orgname"] == self.cleaned_data["orgname2"]:
                       raise forms.ValidationError("Same organization name")
                return self.cleaned_data["orgname2"]

class OrgForm(ModelForm):
        
        def __init__(self, *args, **kwargs):
                super(OrgForm, self).__init__(*args, **kwargs)
                for field_name, field in self.fields.items():
                        field.widget.attrs["class"] = "form-control"

        def clean_orgname(self):
                organization_name = self.cleaned_data["orgname"]
                if Organization.objects.filter(orgname = organization_name).exists():
                        raise forms.ValidationError("Organization already exists")
                return organization_name
        
        class Meta:
                model = Organization
                fields = ["orgname", "orgtypeid", "street", "city", "state", "zipcode", "description"]
                labels = {"orgname": "Organization Name", "orgtypeid": "Organization Type"}


class SignUpForm(UserCreationForm):
        first_name = forms.CharField(max_length=30, required=True)
        last_name = forms.CharField(max_length=30, required=True)
        email = forms.EmailField(max_length=254, required=True)

        class Meta:
                model = User
                fields = ('username','first_name','last_name','email','password1',
                          'password2',)
