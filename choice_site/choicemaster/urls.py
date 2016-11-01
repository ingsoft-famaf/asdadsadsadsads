from django.conf.urls import url
from . import views, ajax
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^add/question/$', views.add_question, name='add_question'),
    url(r'^add/question/(?P<subject_id>[0-9]+)/$',views.add_question_w_subject
        , name='add_question_w_subject'),
    url(r'^add/question/(?P<subject_id>[0-9]+)/(?P<topic_id>[0-9]+)/$',
        views.add_question_w_subject_topic,
        name='add_question_w_subject_topic'),
    url(r'^report/$', views.report, name='report'),

    url(r'^configure1/$', views.configure_exam1, name='configure_exam1'),
    url(r'^configure2/(?P<exam_id>[0-9]+)/$', views.configure_exam2,
        name='configure_exam2'),
    url(r'^configure3/(?P<exam_id>[0-9]+)/$', views.configure_exam3,
        name='configure_exam3'),

    url(r'^ajax/get_correct/$', ajax.get_correct, name='get_correct'),
    url(r'^ajax/edit/autoreport/$', ajax.autoreport, name='AutoReport'),

    url(r'^test/$', views.test_exam, name='test'),
    url(r'^resolve_exam/$', views.resolve_exam, name='resolve_exam'),
    url(r'^resolve_exam/(?P<exam_id>[0-9]+)/$', views.resolve_exam, name='resolve_exam')
]

