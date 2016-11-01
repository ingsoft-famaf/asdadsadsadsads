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

    url(r'^test/$', views.test_exam, name='test'),
    url(r'^generate/$', views.resolve_exam, name='resolve_exam'),
    url(r'^generate/(?P<subject_id>[0-9]+)/(?P<topic_id>[0-9]+)/(?P<timer>[0-9]+)/(?P<quantity>[0-9]+)/(?P<algorithm>[0-1]+)/$',
        views.resolve_exam, name='resolve_exam_')

]

