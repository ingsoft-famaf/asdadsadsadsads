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

def test_exam(request):
    subject = models.Subject.objects.get(pk = 1)
    topic = models.Topic.objects.filter(subject = subject.id)
    context = dict()
    context['subject_id'] = subject.id
    context['subject'] = subject
    context['topic'] = topic
    context['topic_ids'] = topic[0].id
    context['timer'] = 30
    context['quantity'] = 2
    context['algorithm'] = 0
    # exam = ExamView()
    return render(request, 'choicemaster/exam/resolve_exam.html', context)


def resolve_exam(request, subject='', topic_ids={}, timer='', quantity='', algorithm=''):
    
    if request.method != 'POST':

        subject_id = subject
        topic_ids_tmp = topic_ids
        timer_tmp = timer
        quantity_tmp = quantity
        algorithm_tmp = algorithm

        # Create the exam model with all the configurations
        exam = models.Exam.objects.create(exam_subject=self.subject_id,
            exam_quantity_questions=self.remaining, exam_timer=self.timer,
            exam_algorithm=self.algorithm) # TODO Poner el usuario que lo realiza
        
        exam_id = exam.pk
        exam.save()

        kwargs = dict()
        kwargs['subject_id'] = subject_id
        kwargs['topic_ids'] = topic_ids
        kwargs['timer'] = topic_ids
        kwargs['quantity'] = quantity
        kwargs['algorithm'] = topic_ids
        kwargs['exam_id'] = exam.id

        exam_tmp = ExamView(kwargs)

        # We store all the questions of the selected topics
        for item in topic_ids:
            questions_tmp = Topic.objects.filter(id=topic_id)
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
    exam_id = 0
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

    def __init__(self, *args, **kwargs):
        exam_id = kwargs['exam_id']
        subject_id = kwargs['subject_id']
        topic_ids = kwargs['topic_ids']
        timer = kwargs['timer']
        remaining = kwargs['quantity']
        algorithm = kwargs['algorithm']
        mistakes = {}
        initial = {}
        questions = {}
        questions_used = {}
        amount_correct = 0


    def getQuestion(self):
        
        if self.algorithm:
            topic_id = max(mistakes, key = mistakes.get)
            questions_topic = Question.objects.filter(topic = topic_id)
            try:
                question = random.choice(questions_topic)
                self.questions_used[question.id] = question
                del self.questions[question.id]
            except IndexError:
                question = random.choice(self.questions)
                self.questions_used[question.id] = question
                del self.questions[question.id]

        else:
            question = random.choice(self.questions)
            self.questions_used[question.id] = question
            del self.questions[question.id]
            
        return question