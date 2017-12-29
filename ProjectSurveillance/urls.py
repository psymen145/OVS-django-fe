from django.conf.urls import url, include
from . import views, projectviews
from django.contrib.auth.views import login
from django.views.generic import ListView, DetailView
#from ProjectSurveillance.models import Projects

urlpatterns = [
    url(r'^$', views.dashboard),
    url(r'^dashboard/$', views.dashboard, name="dashboard"),
    url(r'^dashboard/update_phase/$', views.update_phase, name='updatephase'),
    url(r'^dashboard/project/$', projectviews.all_projects, name="allprojs"),
    url(r'^dashboard/project/(?P<pk>\d+)$', projectviews.project_details, name="projdetails"),
    url(r'^dashboard/project/detail/ajax_tab', projectviews.project_details_ajax, name="projdetailsajax"),
    url(r'^dashboard/project/update_ajax/$', projectviews.project_details_update, name="projdetailsupdate"),
    url(r'^dashboard/project/update_ajax/activity/$', projectviews.project_details_update_activity, name="projdetailsupdateact"),
    url(r'^dashboard/user/$', views.all_users, name="allusers"),
    url(r'^dashboard/user/(?P<pk>\d+)$', views.user_details, name="userdetails"),
    url(r'^dashboard/user/ajax/$', views.all_users_ajax, name="allusersajax"),
    url(r'^dashboard/user/update_ajax/$', views.user_details_update, name="userdetailsupdate"),
    url(r'^dashboard/user/update_ajax/archivemodal/$', views.user_details_update_modal, name="userdetailsarchivemodal"),
    url(r'^dashboard/user/new/$', views.new_user_form, name="newuser"),
    url(r'^dashboard/project/new/$', views.new_proj_form, name="newproject"),
    url(r'^dashboard/org/new/$', views.new_org_form, name="neworg"),
    url(r'^dashboard/project/ajax/filterchange/$', projectviews.filter_change, name="filterchange"),
    url(r'^dashboard/project/ajax/$', projectviews.all_projects_ajax, name="allprojsajax"),
    url(r'^reports/$', views.reports, name="reports"),
    #url(r'^dashboard/project/$', ListView.as_view(queryset=Projects.objects.all().order_by("projectcatid"), template_name="ProjectSurveillance/projectview.html")),
]
