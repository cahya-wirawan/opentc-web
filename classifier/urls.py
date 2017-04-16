from django.conf.urls import url

from . import views

app_name = 'classifier'

urlpatterns = [
    # ex: /classifier/
    url(r'^$', views.index, name='index'),
    # ex: /classifier/5/
    url(r'^(?P<classifier_id>[0-9]+)/$', views.detail, name='detail'),
    # ex: /classifier/predict/
    url(r'^predict/$', views.predict, name='predict'),
    # ex: /classifier/predict_submit/
    url(r'^predict_submit/$', views.predict_submit, name='predict_submit'),
    # ex: /classifier/predict_result/
    url(r'^predict_result/$', views.predict_result, name='predict_result'),
    # ex: /classifier/request_submit/
    url(r'^request_submit/$', views.request_submit, name='request_submit'),
    # ex: /classifier/request_info/
    url(r'^request_info$', views.request_info, name='request_info'),
]
