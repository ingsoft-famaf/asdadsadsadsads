from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from choicemaster import models
from .forms import UploadFileForm

from .upload import parse_xml_question
from models import Report


@login_required
def index(request, message=''):
    if message:
        context = {'message': message}
    else:
        context = {'message': 'Everything ok!'}
    context['reported'] = Report.objects.exclude(report_state='E').count()

    return render(request, 'choicemaster/index.html', context)


@login_required
@staff_member_required
def add_question(request):
    context = dict()
    context['subjects'] = models.Subject.objects.all()
    return render(request, 'choicemaster/add/question.html', context)


@login_required
@staff_member_required
def add_question_w_subject(request, subject_id):
    subject = models.Subject.objects.filter(id=subject_id)[0]
    topics = models.Topic.objects.filter(subject_id=subject_id)
    context = dict()
    context['subject'] = subject
    context['topics'] = topics
    return render(request, 'choicemaster/add/question/w_subject.html', context)


@login_required
@staff_member_required
def add_question_w_subject_topic(request, subject_id, topic_id, message=''):
    subject = models.Subject.objects.filter(id=subject_id)[0]
    topic = models.Topic.objects.filter(id=topic_id)[0]
    context = dict()
    context['subject'] = subject
    context['topic'] = topic
    if message:
        context['message'] = message
    else:
        context['message'] = 'Everything ok!'

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            result = parse_xml_question(request.FILES['docfile'], topic_id)
            # TODO revisar como hacer el redirect.
            
            if result['status']:
                context['message'] = result['message']
                return render(request, 'choicemaster/index.html',context)
            else:
                context['message'] = result['message']
                return render(request, 'choicemaster/add/question/w_subject'
                    '_topic.html',context)

            
            # return redirect('index')
    else:
        form = UploadFileForm()
        context['form'] = form

    return render(request, 'choicemaster/add/question/w_subject_topic.html',
        context)

def report(request):
    """
    Le paso al template la cantidad de reportes sin ser evaluados que hay en el
    momento.
    """
    context = dict()
    context['reports'] =Report.objects.exclude(report_state="E")
    return render(request, 'choicemaster/report.html', context)

