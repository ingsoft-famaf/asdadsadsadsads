from django.shortcuts import render, redirect, HttpResponse, render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from choicemaster import models
from .forms import UploadFileForm, ConfigureExamForm2, ExamForm
from django.views import View

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


@login_required
def configure_exam2(request):
    if request.method == 'POST':
        form = ConfigureExamForm2(request.POST)
        if form.is_valid():
            subject = request.POST.get('subject')
            mult_topics = request.POST.getlist('mult_topics[]')
            timer = request.POST.get('timer')
            quantity = request.POST.get('quantity')
            # GENERAR EXAMEN
    else:
        form = ConfigureExamForm2()
    return render(request, 'choicemaster/exam/configure_exam.html', {'form': form})

''' Views to configure the exam - Las hace nacho las dejo para guiarme 

#@login_required
def configure_exam_subject(request):
    context = dict()
    context['subjects'] = models.Subject.objects.all()
    return render(request, 'choicemaster/exam/configure_exam.html', context)


#@login_required
def configure_exam_topic(request, subject_id):
    subject = models.Subject.objects.filter(id=subject_id)[0]
    topics = models.Topic.objects.filter(subject_id=subject_id)
    context = dict()
    context['subject'] = subject
    context['topics'] = topics
    return render(request, 'choicemaster/exam/configure_topic.html', context)


#@login_required
def configure_exam(request, subject_id ='', topic_ids =''):
    
    subject = models.Subject.objects.filter(id=subject_id)[0]
    for item in topic_ids
    topic = models.Topic.objects.filter(id=topic_id)[0]
    context = dict()
    context['subject'] = subject
    context['topics'] = topic

    if request.method == 'POST':
        form = ConfigureForm(request.POST)
        if form.is_valid():
            form.save()
            timer = request.POST.get('timer')
            quantity = request.POST.get('quantity')
            context['timer'] = timer
            context['quantity'] = quantity
            exam = Exam.objects.create(exam_quantity_questions = quantity, exam_timer = timer,
                    exam_subject = subject_id, exam_topics)
        return render('choicemaster/exam/generate_exam.html', context)
    else:
        context['form'] = ConfigureForm()
        context['request'] = request
        return render(request, 'choicemaster/exam/configure_timer_quantity.html', context)


def generate_exam(request, subject_id ='', topic_id ='', timer='', quantity=''):

    if request.method == 'POST':
        request.POST.get('')

    else:
        context['form'] = GenerateExamForm(question)
        context['request'] = request
        return render(request, 'choicemaster/exam/resolve.html', context)
    questions = 
'''
def test_exam(request):
    subject = models.Subject.objects.get(pk = 1)
    topic = models.Topic.objects.filter(subject = subject.id)
    context = dict()
    context['subject'] = subject
    context['topic'] = topic
    context['topic_ids'] = topic[0].id
    context['timer'] = 30
    context['quantity'] = 2
    context['algorithm'] = 0
    return render(request, 'choicemaster/exam/resolve_exam.html', context)




class ExamView(View):
    form_class = ExamForm
    template_name = 'choicemaster/exam/resolve_exam.html'
    exam_id = 0
    initial = {}
    questions = {}
    subject_id = ''
    topic_ids = {}
    timer = 1
    remaining = 0
    algorithm = 0
    mistakes = {}
    amount_correct = 0
    show_answer = 1

    def get(self, request, *args, **kwargs):
        subject = kwargs['subject']
        self.subject_id = subject.id
        self.topic_ids = kwargs['topic_ids']
        self.timer = kwargs['timer']
        self.remaining = kwargs['quantity']
        self.algorithm = kwargs['algorithm']
        
        # Create the exam model with all the configurations
        exam = Exam.objects.create(exam_subject = self.subject_id,
            exam_quantity_questions = self.remaining, exam_timer = self.timer,
            exam_algorithm = self.algorithm)
        
        self.exam_id = exam.pk
        exam.save()

        # We store all the questions of the selected topics
        for item in topic_ids:
            questions_tmp = Topic.objects.filter(id = topic_id)
            for q in questions_tmp:
                self.questions[str(q.id)] = q
            
        # Select a random question for the first one.
        question = getQuestion()
        self.remaining =- 1

        # Generate the form
        self.initial = {'question': question.id}
        form = self.form_class(initial=self.initial)
        context['subject'] = subject.subject_title
        context['topic'] = question.topic
        context['form'] = form
        context['question'] = question

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            answer_id = request.POST.get('answer')
            answer = Answer.objects.get(pk = answer_id)
            question_id = kwargs['question'].id
            topic_id = kwargs['topic_id']
            correct_answer = Answer.objects.get(question = question_id, correct = True)

            if show_answer:            
                # Generate the snapshot of the answer
                snap = QuestionSnapshot.objects.create(exam = self.exam.id, question = question_id,
                    choosen_answer = answer.answer_text, correct_answer = correct_answer.answer_text,
                    choice_correct = correct_answer.answer_text.equals(answer.answer_text))
                snap.save()
                show_answer = 0
                kwargs['snap'] = snap
                return render(request, 'choicemaster/exam/show_result.hmtl', kwargs)
            
            self.remaining=- 1

            if not answer.correct:
                mistakes[topic_id] += 1
            else:
                self.amount_correct += 1

            if self.remaining:
                # Get the next question
                question = getQuestion()
                topic_id = question.topic
                # Generate the form
                self.initial = {'question': question.id}
                form = self.form_class(initial=self.initial)
                
                # Build the context for the next iteration
                context = dict()
                context['question'] = question
                context['topic_id'] = topic_id
                context['form'] = form

                return render(request, self.template_name, context)
            else:
                # End of the exam
                exam = Exam.objects.get(pk = self.exam_id)
                exam.result = self.amount_correct
                exam.save()

                # Return to the index page with the amount of correct answers on the message board
                return render(request, 'index', {message: self.amount_correct})
        
        # TODO Check if it is needed the context here
        return render(request, self.template_name, {'form': form})

    def getQuestion(self):
        
        if self.algorithm:
            topic_id = max(mistakes, key = mistakes.get)
            questions_topic = Question.objects.filter(topic = topic_id)
            try:
                question = random.choice(questions_topic)
                del self.questions[question.id]
            except IndexError:
                question = random.choice(self.questions)
                del self.questions[question.id]

        else:
            question = random.choice(self.questions)
            del self.questions[question.id]
            
        return question