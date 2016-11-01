from django.shortcuts import render, redirect, HttpResponse, render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from choicemaster import models
from .forms import *
from django.views import View
import random
import ipdb
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


# Nuevos configure
@login_required
def configure_exam1(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject_id = request.POST.get('subject')
            exam = models.Exam(user=models.User.objects.get(pk=1))
            # ipdb.set_trace()
            exam.subject = models.Subject.objects.get(pk=subject_id)
            exam.save()
            return redirect('configure_exam2', exam_id=exam.id)
    else:
        form = SubjectForm()
    return render(request, 'choicemaster/exam/configure_exam1.html',
                  {'form': form})


@login_required
def configure_exam2(request, exam_id):
    e = models.Exam.objects.get(pk=exam_id)
    if request.method == 'POST':
        form = MultipleTopicForm(request.POST)
        if form.is_valid():
            topic_ids = request.POST.getlist('topic')
            for idt in topic_ids:
                t = models.Topic.objects.get(pk=idt)
                e.topic.add(t)
            e.save()
            redirect('configure_exam3', exam_id=exam_id)
    else:
        #ipdb.set_trace()
        form = MultipleTopicForm(e.subject.id)
    return render(request, 'choicemaster/exam/configure_exam2.html',
                  {'form': form})


@login_required
def configure_exam3(request, exam_id):
    if request.method == 'POST':
        form = ConfigForm(request.POST)
        if form.is_valid():
            quantity = request.POST.get('quantity')
            timer = request.POST.get('timer')
            e = models.Exam.objects.get(pk=exam_id)
            e.quantity_questions = quantity
            e.timer = timer
            e.save()
            redirect('generate_exam', exam_id=exam_id)
    else:
        form = ConfigForm()
    return render(request, 'choicemaster/exam/configure_exam2.html',
                  {'form': form})


# Nuevos configure


def test_exam(request):
    subject = models.Subject.objects.get(pk=1)
    topic = models.Topic.objects.filter(subject=subject.id)
    context = dict()
    context['subject'] = subject
    context['subject_id'] = subject.id
    context['topic'] = topic
    context['topic_ids'] = topic[0].id
    context['timer'] = 30
    context['quantity'] = 2
    context['algorithm'] = 0
    # exam = ExamView()
    return render(request, 'choicemaster/exam/resolve_exam.html', context)


def resolve_exam(request, subject_id='', topic_id='', timer='', quantity='', algorithm='', exam_tmp=''):
    # ipdb.set_trace()
    if request.method != 'POST':
        '''
        subject_id_tmp = subject
        topic_ids_tmp = topic_ids
        timer_tmp = timer
        quantity_tmp = quantity
        algorithm_tmp = algorithm
        '''
        subject =models.Subject.objects.get(pk=subject_id)

        # Create the exam model with all the configurations
        exam = models.Exam.objects.create(user=models.User.objects.get(pk=1),
            exam_subject=models.Subject.objects.get(pk=subject_id),
            exam_quantity_questions=quantity, exam_timer=timer,
            exam_algorithm=algorithm) # TODO Poner el usuario que lo realiza
        
        exam_id = exam.id
        exam.save()
        a = []   # Just to check
        a.append(1) # To check
        kwargs = dict()
        kwargs['subject_id'] = subject_id
        kwargs['topic_ids'] = a
        kwargs['timer'] = timer
        kwargs['quantity'] = quantity
        kwargs['algorithm'] = algorithm
        kwargs['exam'] = exam

        exam_tmp = ExamView(subject_id, a, timer, quantity, algorithm, exam)

        topic_ids = [topic_id]
        # We store all the questions of the selected topics
        ipdb.set_trace()
        for item in topic_ids:
            questions_tmp = models.Question.objects.filter(topic=models.Topic.objects.get(pk=item))
            for q in questions_tmp:
                exam_tmp.questions[str(q.id)] = q
            
        # Select a random question for the first one.
        question = exam_tmp.getQuestion()
        exam_tmp.remaining =- 1

        # Generate the form
        exam_tmp.initial = {'question': question.id}
        form = exam_tmp.form_class(initial=exam_tmp.initial)
        
        context = dict()
        context['subject'] = subject
        context['topic'] = question.topic
        context['form'] = form
        context['question'] = question
        context['exam_tmp'] = exam_tmp

        return render(request, 'choicemaster/exam/resolve_exam.html', context)

    else:
        
        form = ExamForm(request.POST)
        if form.is_valid():
            exam_tmp = request.POST.get('exam_tmp')
            answer_id = request.POST.get('answer')
            answer = Answer.objects.get(pk=answer_id)
            question_id = answer.question
            # topic_id = kwargs['topic_id'] TODO
            correct_answer = Answer.objects.get(question=question_id, correct=True)

            # Generate the snapshot of the answer
            snap = QuestionSnapshot.objects.create(exam=self.exam.id, question=question_id,
                choosen_answer=answer.answer_text, correct_answer=correct_answer.answer_text,
                choice_correct=correct_answer.answer_text.equals(answer.answer_text))
            snap.save()

            exam_tmp.remaining=- 1

            if not answer.correct:
                exam_tmp.mistakes[topic_id] += 1
            else:
                exam_tmp.amount_correct += 1

            if exam_tmp.remaining:
                # Get the next question
                question = exam_tmp.getQuestion()
                topic_id = question.topic
                # Generate the form
                exam_tmp.initial = {'question': question.id}
                form = exam_tmp.form_class(initial=self.initial)
                
                # Build the context for the next iteration
                context = dict()
                context['question'] = question
                context['topic_id'] = topic_id
                context['form'] = form

                return render(request, 'choicemaster/exam/resolve_exam.html', context)
            else:
                # End of the exam
                exam = Exam.objects.get(pk = self.exam_id)
                exam.result = exam_tmp.amount_correct
                exam.save()

                # Return to the index page with the amount of correct answers on the message board
                return render(request, 'index', {message: self.amount_correct})
        
        # TODO Check if it is needed the context here
        return render(request, 'choicemaster/exam/resolve_exam.html', {'form': form})



class ExamView(View):
    form_class = ExamForm
    template_name = 'choicemaster/exam/resolve_exam.html'
    exam = 0
    initial = {}
    questions = {}
    questions_used = {}
    subject_id = ''
    topic_ids = {}
    timer = 1
    remaining = 0
    algorithm = 0
    mistakes = {}
    amount_correct = 0

    def __init__(self, subject_id, topic_ids, timer, quantity, algorithm, exam):
        self.subject_id = subject_id
        self.exam =  exam
        self.topic_ids = topic_ids
        self.timer = timer
        self.remaining = quantity
        self.algorithm = 0
        self.mistakes = {}
        self.initial = {}
        self.questions = {}
        self.questions_used = {}
        self.amount_correct = 0


    def getQuestion(self):
        #ipdb.set_trace()
        if self.algorithm:
            topic_id = max(self.mistakes, key=self.mistakes.get)
            questions_topic = Question.objects.filter(topic = topic_id)
            try:
                question = self.questions[random.choice(self.questions.keys())]
                self.questions_used[str(question.id)] = question
                del self.questions[str(question.id)]
            except IndexError:
                question = self.questions[random.choice(self.questions.keys())]
                self.questions_used[str(question.id)] = question
                del self.questions[str(question.id)]

        else:
            index = random.choice(self.questions.keys())
            question = self.questions[index]
            self.questions_used[str(question.id)] = question
            del self.questions[str(question.id)]
            
        return question