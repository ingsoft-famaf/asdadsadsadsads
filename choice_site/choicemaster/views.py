from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from choicemaster import models
from .forms import *

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
    if request.method == 'POST':
        form = UploadQuestionForm(request.POST, request.FILES)
        if form.is_valid():
            topic = request.POST.get('topic')
            file = request.FILES['xmlfile']
            if topic > 0:
                parse_xml_question(file, topic)
            redirect(index)
        else:
            print form.errors
            redirect(add_question)
    else:
        form = UploadQuestionForm()
        context['form'] = form
    return render(request, 'choicemaster/add/question.html', context)


def report(request):
    # TODO Check function. Documentation doesn't match implementation. Spanish?
    """
    Le paso al template la cantidad de reportes sin ser evaluados que hay en el
    momento.
    """
    context = dict()
    context['reports'] = Report.objects.all()
    return render(request, 'choicemaster/report.html', context)

