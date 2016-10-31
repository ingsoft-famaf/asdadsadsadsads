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

    url(r'^configure/$', views.configure_exam2, name='configure_exam'),
    url(r'^ajax/get_checkboxes/$', ajax.get_checkboxes, name='ajax_get_checkoxes'),
    url(r'^test/$', views.test_exam, name='test'),
    url(r'^generate/$', views.resolve_exam, name='resolve_exam')
]

