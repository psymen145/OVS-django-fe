from django.conf.urls import url,include
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^$', views.visual, name="analysis_visuals"),
    url(r'^new/$', views.new_analysis_proj, name="new_analysis_proj"),
    url(r'^inspect/$', views.analysis_proj_view, name="analysis_proj_view"),
    url(r'^inspect/(?P<pk>\d+)$', views.indiv_analysis_proj_view, name="indivanaproj"),
]
