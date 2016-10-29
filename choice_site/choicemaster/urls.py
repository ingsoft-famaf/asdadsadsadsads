from django.conf.urls import url
from . import views
from . import ajax

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^add/question/$', views.add_question, name='add_question'),
    url(r'^add/question/(?P<subject_id>[0-9]+)/$',views.add_question_w_subject
        , name='add_question_w_subject'),
    url(r'^add/question/(?P<subject_id>[0-9]+)/(?P<topic_id>[0-9]+)/$',
        views.add_question_w_subject_topic,
        name='add_question_w_sdeect_topic'),
    url(r'^report/$', views.report, name='report'),
    url(r'^ajax/delete/$', ajax.delete_report, name="delete_report")

]
