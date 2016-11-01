from django.shortcuts import render, redirect, HttpResponse, render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from choicemaster import models
from .forms import *
from django.views import View
import random
from .upload import parse_xml_question
from models import Report


@login_required
def index(request, message=''):
    '''
    Simple index view that renders a message passed by some request and
    returns it as a HTML response
    '''
    if message:
        context = {'message': message}
    else:
        context = {'message': 'Everything ok!'}
    context['reported'] = Report.objects.exclude(report_state='E').count()

    return render(request, 'choicemaster/index.html', context)


@login_required
@staff_member_required
def add_question(request):
    '''
    Get the list of available subjects from request and return them rendered
    as a response with the corresponding template
    '''
    context = dict()
    context['subjects'] = models.Subject.objects.all()
    return render(request, 'choicemaster/add/question.html', context)


@login_required
@staff_member_required
def add_question_w_subject(request, subject_id):
    '''
    Get list of topics related to the given subject_id and pass them to the
    corresponding template
    '''
    subject = models.Subject.objects.filter(id=subject_id)[0]
    topics = models.Topic.objects.filter(subject_id=subject_id)
    context = dict()
    context['subject'] = subject
    context['topics'] = topics
    return render(request, 'choicemaster/add/question/w_subject.html', context)


@login_required
@staff_member_required
def add_question_w_subject_topic(request, subject_id, topic_id, message=''):
    '''
    Get one or more questions from a file and load them into the given subject
    and topic. Check that the form in request is in correct format so to render
    it and return the context generated by the call to the parse method
    '''
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

            if result['status']:
                context['message'] = result['message']
                return render(request, 'choicemaster/index.html', context)
            else:
                context['message'] = result['message']
                return render(request,
                              'choicemaster/add/question/w_subject_topic.html',
                              context)

    else:
        form = UploadFileForm()
        context['form'] = form

    return render(request, 'choicemaster/add/question/w_subject_topic.html',
                  context)


def report(request):
    """
    Pass on to the reports template, the number of reports not evaluated so far
    """
    context = dict()
    context['reports'] = Report.objects.all()
    return render(request, 'choicemaster/report.html', context)


# Nuevos configure
@login_required
def configure_exam1(request):
    '''
    First view regarding an exam configuration. Look for a form from the input
    request. Retrieve the subject from the POST data and create an exam
    instance related to the user to redirect it to the template in which he
    chooses the topics he wants to include in the exam
    '''
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject_id = request.POST.get('subject')
            exam = models.Exam(user=models.User.objects.get(pk=1))
            exam.subject = models.Subject.objects.get(pk=subject_id)
            exam.save()
            return redirect('configure_exam2', exam_id=exam.id)
    else:
        form = SubjectForm()
    return render(request, 'choicemaster/exam/configure_exam1.html',
                  {'form': form})


@login_required
def configure_exam2(request, exam_id):
    '''
    Get a list of topics from request and include them in the exam given by
    exam_id. Save it in the exam object and redirect it to the next exam
    configuration template
    '''
    e = models.Exam.objects.get(pk=exam_id)
    ids = models.Subject.objects.get(pk=e.subject.id).id
    if request.method == 'POST':
        form = MultipleTopicForm(ids, request.POST)
        if form.is_valid():
            topic_ids = request.POST.getlist('topic')
            for idt in topic_ids:
                t = models.Topic.objects.get(pk=idt)
                e.topic.add(t)
            e.save()
            return redirect('configure_exam3', exam_id=exam_id)
    else:
        form = MultipleTopicForm(e.subject.id)
    return render(request, 'choicemaster/exam/configure_exam2.html',
                  {'form': form, 'exam_id': exam_id})


@login_required
def configure_exam3(request, exam_id):
    '''
    Add questions to the exam object according to the number required by the
    user. Raise an error message in case the required number of questions is
    greater than the number of questions available in the database for such
    subject
    '''
    e = models.Exam.objects.get(pk=exam_id)
    max_quantity = 0
    for t in e.topic.all():
        questions = models.Question.objects.filter(topic=t.id)
        max_quantity += len(questions)
    if request.method == 'POST':
        form = ConfigForm(max_quantity, request.POST)
        if form.is_valid():
            quantity = request.POST.get('quantity')
            timer = request.POST.get('timer')
            e = models.Exam.objects.get(pk=exam_id)
            e.exam_quantity_questions = quantity
            e.exam_timer = timer
            e.save()
            return redirect('resolve_exam', exam_id=exam_id)
    else:
        form = ConfigForm(max_quantity)
    return render(request, 'choicemaster/exam/configure_exam3.html',
                  {'form': form, 'exam_id': exam_id})

# Define a global exams variable
global_exams = None


def resolve_exam(request, exam_id=''):
    '''
    View to actually solve the exam. Consider two cases:

    1. request has been sent for the first time on this exam, in which case it
    contains the information about the exam settings (subject, timer, quantity,
    algorithm). Generate an ExamView for such settings, fill the exam object
    with questions and then choose the first question from the first topic in
    order to display it in the resolve_exam template

    2. request method is POST, which means it has been triggered by a solution
    submitted in the front end. Check whether the answer given by the user is
    right or wrong, and create a snapshot accordingly. Keep a record of right
    and wrong guesses to be used in the algorithm to display questions
    afterwards. Also, keep track of remaining time and use it to pass to the
    next question in case it is over.
    '''
    if request.method != 'POST':
    
        exam = models.Exam.objects.get(pk=exam_id)
        subject = exam.subject
        timer = exam.exam_timer
        quantity = exam.exam_quantity_questions
        algorithm = exam.exam_algorithm


        exam_tmp = ExamView(subject.id, timer, quantity, algorithm, exam.id)

        topic_ids = exam.topic.all() # TODO
        # We store all the questions of the selected topics
        for item in topic_ids:
            questions_tmp = models.Question.objects.filter(topic=models.Topic.objects.get(pk=item.id))
            exam_tmp.mistakes[str(item.id)] = item.id
            for q in questions_tmp:
                exam_tmp.questions[str(q.id)] = q
            
        # Select a random question for the first one.
        question = exam_tmp.getQuestion()

        # Generate the form
        form = exam_tmp.form_class(question=question.id)
        
        context = dict()
        context['subject'] = subject
        context['topic'] = question.topic
        context['form'] = form
        context['question'] = question
        
        global global_exams
        global_exams = exam_tmp

        return render(request, 'choicemaster/exam/resolve_exam.html', context)

    else:
        form = ExamForm(request.POST)
        answer_id = request.POST.get('answer')
        exam_tmp = global_exams

        answer = Answer.objects.get(pk=answer_id)
        
        question = answer.question
        topic_id = question.topic.id
        answers = Answer.objects.filter(question=question.id)
        correct_answer = answers.filter(correct=True)[0]


        value = (correct_answer.id == answer.id)
        # Generate the snapshot of the answer
        snap = QuestionSnapshot.objects.create(exam=models.Exam.objects.get(pk=exam_tmp.exam), question=question,
            chosen_answer=answer.answer_text, correct_answer=correct_answer.answer_text,
            choice_correct=value)
        snap.save()

        exam_tmp.remaining -= 1

        if not answer.correct:
            exam_tmp.mistakes[str(topic_id)] += 1
        else:
            exam_tmp.amount_correct += 1

        if exam_tmp.remaining:
            # Get the next question
            question = exam_tmp.getQuestion()
            # Generate the form
            form = ExamForm(question=question.id)
            
            # Build the context for the next iteration
            context = dict()
            context['question'] = question
            context['form'] = form

            context['questions_used'] = exam_tmp.questions_used
            context['subject'] = models.Subject.objects.get(pk=exam_tmp.subject_id)
            context['question'] = question

            return render(request, 'choicemaster/exam/resolve_exam.html', context)
        else:
            # End of the exam
            exam = models.Exam.objects.get(pk=exam_tmp.exam)
            exam.result = exam_tmp.amount_correct
            exam.save()

            # Return to the index page with the amount of correct answers on the message board
            message = "Of " + str(models.Exam.objects.get(pk=exam_tmp.exam).exam_quantity_questions) +\
                " questions, correct: " + str(exam_tmp.amount_correct)
            return render(request, 'choicemaster/index.html', {'message': message})
    
        # TODO Check if it is needed the context here
        #return render(request, 'choicemaster/exam/resolve_exam.html', {'form': form})




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

    def __init__(self, subject_id, timer, quantity, algorithm, exam):
        self.subject_id = subject_id
        self.exam =  exam
        self.timer = timer
        self.remaining = quantity
        self.algorithm = 0
        self.mistakes = {}
        self.initial = {}
        self.questions = {}
        self.questions_used = {}
        self.amount_correct = 0


    def getQuestion(self):
    '''
    Get a question from the list of questions of the given topics. Consider the
    cases when the exam has the algorithm mode on and off as separate.
    '''
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