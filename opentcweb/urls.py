"""opentc_web URL Configuration

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
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from classifier import views

urlpatterns = [
    # api
    url(r'^api/v1/prediction/$', views.prediction, name='prediction'),
    url(r'^api/v1/classifications/$', views.classifications_collection, name='classifications_collection'),
    url(r'^api/v1/classifications/(?P<pk>[0-9]+)$', views.classifications_element, name='classifications_element'),
    url(r'^api/v1/get_random_article/$', views.get_random_article, name='get_random_article'),
    url(r'^$', RedirectView.as_view(url='/demo')),
    # ex: /demo/
    url(r'^demo/$', views.predict, name='predict'),
    url(r'^report/$', views.request_info, name='request_info'),
    url(r'^classifier/', include('classifier.urls')),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/login/$', auth_views.LoginView.as_view()),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
