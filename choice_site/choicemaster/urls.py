from django.conf.urls import url
from . import views, ajax

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'ajax_view/$', ajax.ajax_view, name='ajax_view'),
    url(r'^add/question/$', views.add_question, name='add_question'),
    url(r'^report/$', views.report, name='report')
]
