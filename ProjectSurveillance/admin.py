from django.contrib import admin
from .models import *

myModels = [Component, Accesspath, Dataset, DetailType, OrganizationType, Organization, ProjectDatasetRequest,
            ProjectVariable, Project, UserOrganization, UserProject, VSUser, VariableDataset,
            Variable, WorkPhase, WorkStep, ProjectActivity]

admin.site.register(myModels)

