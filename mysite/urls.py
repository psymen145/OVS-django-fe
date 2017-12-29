"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include, handler404, handler500
from django.contrib import admin
from django.contrib.auth import views as auth_views
from ProjectSurveillance import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include('ProjectSurveillance.urls')),
    url(r'^analysis/', include('Analysis.urls')),
    url(r'^login/$', auth_views.login, {'template_name': 'ProjectSurveillance/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^signup/validate_username/$', views.validate_username, name='validate_username'),
]

handler404 = views.error_404
handler500 = views.error_500