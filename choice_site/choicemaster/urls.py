from django.conf.urls import url
from . import views, ajax

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^add/question/$', views.add_question, name='add_question'),
    url(r'^suggestion/redirect/$', views.redirect_suggestion,
        name='Suggestion'),

    url(r'^report/$', views.report, name='report'),
    url(r'^suggestions/$', views.suggestions, name='suggestions'),

    url(r'ajax/get_quantity_suggestions/$',
        ajax.get_quantity_suggestions,
        name='get_quantity_suggestions'),
    url(r'ajax_view/$', ajax.ajax_view, name='ajax_view'),
    url(r'^ajax/delete/report$', ajax.delete_report, name="delete_report"),
    url(r'^ajax/delete/question/$', ajax.delete_question,
        name="delete_question"),
    url(r'^ajax/delete/answer/$', ajax.delete_answer, name="delete_answer"),
    url(r'^ajax/edit/question/$', ajax.edit_question, name="edit_question"),
    url(r'^ajax/edit/answer/$', ajax.edit_ans, name="edit_answer"),
    url(r'^ajax/get_correct/$', ajax.get_correct, name='get_correct'),
    url(r'^ajax/edit/autoreport/$', ajax.autoreport, name='autoreport'),
    url(r'^ajax/edit/reporting/$', ajax.add_report, name='add_report'),
    url(r'^ajax/edit/correct/$', ajax.edit_correct, name='edit_correct'),
    url(r'^ajax/accept/suggestion/$', ajax.accept_suggestion,
        name='accept_suggestion'),

    url(r'^configure1/$', views.configure_exam1, name='configure_exam1'),
    url(r'^configure2/(?P<exam_id>[0-9]+)/$', views.configure_exam2,
        name='configure_exam2'),
    url(r'^configure3/(?P<exam_id>[0-9]+)/$', views.configure_exam3,
        name='configure_exam3'),

    url(r'^resolve_exam/$', views.resolve_exam, name='resolve_exam'),
    url(r'^resolve_exam/(?P<exam_id>[0-9]+)/$', views.resolve_exam,
        name='resolve_exam'),

    url(r'^statistics/subjects/$', views.subjects_statistics,
        name='subject_statistics'),
    url(r'^statistics/subject/(?P<subject_id>[0-9]+)/$', views.subject_detail,
        name='exam_detail'),
    url(r'^statistics/exam/(?P<exam_id>[0-9]+)/$', views.exam_detail,
        name='exam_detail'),

    url(r'^ajax/suggestion/send/$', ajax.suggestion, name='Send suggestion')
]
