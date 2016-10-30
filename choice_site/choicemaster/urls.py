from django.conf.urls import url
from . import views
from ajax_select import urls as ajax_select_urls

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^add/question/$', views.add_question, name='add_question'),
    url(r'^add/question/(?P<subject_id>[0-9]+)/$',views.add_question_w_subject
        , name='add_question_w_subject'),
    url(r'^add/question/(?P<subject_id>[0-9]+)/(?P<topic_id>[0-9]+)/$',
        views.add_question_w_subject_topic,
        name='add_question_w_subject_topic'),
    url(r'^report/$', views.report, name='report'),
    
]
'''
url(r'^configure/$', views.configure_exam_subject, name='configure_subject'),

url(r'^configure/(?P<subject_id>[0-9]+)/$',views.configure_exam_topic
    , name='configure_exam_w_subject'),

url(r'^configure/(?P<subject_id>[0-9]+)/(?P<topic_id>[0-9]+)/$',
    views.configure_exam,
    name='configure_timer_quantity'),
'''
