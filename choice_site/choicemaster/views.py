from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from lxml import etree
from choicemaster import models
from .forms import UploadFileForm

# Imaginary function to handle an uploaded file.
from .upload import parse_xml_question


@login_required
def index(request):
    return render(request, 'choicemaster/index.html')


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
def add_question_w_subject_topic(request, subject_id, topic_id):
    subject = models.Subject.objects.filter(id=subject_id)[0]
    topic = models.Topic.objects.filter(id=topic_id)[0]
    context = dict()
    context['subject'] = subject
    context['topic'] = topic
    return render(request, 'choicemaster/add/question/w_subject_topic.html',
        context)


@login_required
@staff_member_required
def upload_xml(request, subject_id, topic_id):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            response = parse_xml_question(request.FILES['file'], topic_id)
            if response == True:
                return redirect(index)
            else:
                return HttpResponse('An error occurred while loading the file') 
    else:
        form = UploadFileForm()

    return render(request, 'choicemaster/add/question/w_subject_topic.html',
        {'form': form, 'subject': models.Subject.objects.filter(subject_id=subject_id),
        'topic': models.Topic.objects.filter(topic_id=topic_id)})
