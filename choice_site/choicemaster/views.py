from django.shortcuts import render, redirect, HttpResponse, render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from choicemaster import models
from .forms import UploadFileForm, ConfigureExamForm, AjaxForm

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
                return render(request, 'choicemaster/add/question/w_subject_topic.html',context)

            
            # return redirect('index')
    else:
        form = UploadFileForm()
        context['form'] = form

    return render(request, 'choicemaster/add/question/w_subject_topic.html',
        context)

def report(request):
    # TODO Check function. Documentation doesn't match implementation. Spanish?
    """
    Le paso al template la cantidad de reportes sin ser evaluados que hay en el
    momento.
    """
    context = dict()
    context['reports'] = Report.objects.all()
    return render(request, 'choicemaster/report.html', context)

def configure_exam(request, subject_id =''):
    if request.method == 'POST':
        form = ConfigureExamForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'choicemaster/index.html')
    else:
        context = dict()
        context = { 'formid' : 'createform',
                   'submiturl' : "configure_exam",
                   'btntxt' : "Submit form",
                    'jsurl' : 'djhform.js' }
        context['form'] = AjaxForm().ajaxRequest(request) # Magic!
        context['request'] = request
        # form = ConfigureExamForm()
        if request.GET:
            '''
            This is an AJAX request with form parameters set.
            Generate a form snippet here, so don't use the entire template
            '''
            return HttpResponse(context["form"].as_table(), content_type="application/xhtml")        
        else:
            '''
            Generate a brand new form
            '''
        return render_to_response('choicemaster/exam/configure_exam_two.html', context)

#class Create(generic.CreateView):
#    template_name = "configure_exam.html"
#    form_class = ConfigureExamForm
#    success_url = 'create'

#create = Create.as_view()


def javascript(request):
    '''
    This view generates the javascript for the form.  The javascript can be served as
    a static file, but this view injects the form url for the script to call back to the server.
    This could be hardcoded into the javscript if you'd like.
    
    The javascript handles hierarchical field selection actions.  On each selection it calls back
    to the form url, which returns html snippets of the new form fields.
    The javascript then replaces the existing form fields with the new ones.
    '''
    params = { 'formid' : 'createform',
               'ajaxurl': ''
             }
    return render_to_response('choicemaster/exam/djhform.js', params, content_type='application/javascript')