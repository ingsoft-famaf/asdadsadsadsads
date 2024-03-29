import sys
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from choicemaster import models
from .forms import *
from django.http.response import HttpResponse
from .upload import parse_xml_question
from .exam_functions import get_question, get_mistakes
from .models import Report, Question, Answer, Subject
from graphos.sources.simple import SimpleDataSource
from graphos.renderers.gchart import LineChart
import json


@login_required
def index(request, message=''):
    """
    Simple index view that renders a message passed by some request and
    returns it as a HTML response
    :param request: Request, str
    :return: View
    """
    if message:
        context = {'message': message}
    else:
        context = {'message': 'Everything ok!'}
    context['reported'] = Report.objects.exclude(report_state='E').count()

    return render(request, 'choicemaster/index.html', context)


def redirect_suggestion(request):
    context = {'message': 'Suggestion submitted successfully'}
    return render(request, 'choicemaster/index.html', context)


@login_required
def add_question(request):
    """
    Get the list of available subjects from request and return them rendered
    as a response with the corresponding template
    :param request: Request
    :return: View
    """
    context = dict()
    if request.user.is_staff:
        if request.method == 'POST':
            form = UploadQuestionForm(request.POST, request.FILES)
            # if form.is_valid():
            topic = request.POST.get('topic')
            file = request.FILES['xmlfile']
            if topic > 0:
                result = parse_xml_question(file, topic)
                if result['status']:
                    return redirect('index')
                else:
                    form = UploadQuestionForm()
        else:
            form = UploadQuestionForm()
            context['form'] = form

        return render(request, 'choicemaster/add/question.html', context)

    else:
        form = SuggestQuestionForm()
        context['form'] = form
        return render(request, 'choicemaster/add/suggestion.html', context)


def report(request):
    """
    Pass on to the reports template, the number of reports not evaluated so far
    :param request: Request
    :return: View
    """
    context = dict()
    context['reports'] = Report.objects.exclude(report_state="E")
    return render(request, 'choicemaster/report.html', context)


def suggestions(request):
    """
    Pass on to the suggested questions template, the number of questions
    suggested so far
    :param request: Request
    :return: View
    """
    context = dict()
    context['questions'] = models.Question.objects.filter(available=False)
    return render(request, 'choicemaster/suggestions.html', context)


# Nuevos configure
@login_required
def configure_exam1(request):
    """
    First view regarding an exam configuration. Look for a form from the input
    request. Retrieve the subject from the POST data and create an exam
    instance related to the user to redirect it to the template in which he
    chooses the topics he wants to include in the exam
    :param request: Request
    :return: View
    """
    if request.method == 'POST':
        user = None
        if request.user.is_authenticated():
            user = request.user
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject_id = request.POST.get('subject')
            exam = models.Exam(user=user)
            exam.subject = models.Subject.objects.get(pk=subject_id)
            exam.save()
            return redirect('configure_exam2', exam_id=exam.id)
    else:
        form = SubjectForm()
        return render(request, 'choicemaster/exam/configure_exam1.html',
                      {'form': form})


@login_required
def configure_exam2(request, exam_id):
    """
    Get a list of topics from request and include them in the exam given by
    exam_id. Save it in the exam object and redirect it to the next exam
    configuration template
    :param request: Request, str
    :return: View
    """
    e = models.Exam.objects.get(pk=exam_id)
    if not e.closed:
        ids = e.subject.id
        context = dict()
        context['subject_text'] = e.subject.subject_title
        context['exam_id'] = exam_id
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

        context['form'] = form
        return render(
            request,
            'choicemaster/exam/configure_exam2.html',
            context)
    else:
        message = "You have already taken that exam." \
            + "Please create a new one from the 'Take an exam' section"
        return render(request, 'choicemaster/index.html', {'message': message})


@login_required
def configure_exam3(request, exam_id):
    """
    Add questions to the exam object according to the number required by the
    user. Raise an error message in case the required number of questions is
    greater than the number of questions available in the database for such
    subject
    :param request: Request, str
    :return: View
    """
    e = models.Exam.objects.get(pk=exam_id)
    if not e.closed:
        max_quantity = 0
        context = dict()
        context['subject_text'] = e.subject.subject_title
        context['exam_id'] = exam_id
        context['topics'] = e.topic.all()

        for t in e.topic.all():
            questions = models.Question.objects.filter(
                topic=t.id, available=True)
            max_quantity += len(questions)
        if request.method == 'POST':
            form = ConfigForm(max_quantity, request.POST)
            if form.is_valid():
                quantity = request.POST.get('quantity')
                timer = request.POST.get('timer')
                algorithm = request.POST.get('algorithm')
                e = models.Exam.objects.get(pk=exam_id)
                e.exam_quantity_questions = quantity
                e.remaining = quantity
                e.exam_timer = timer
                e.exam_algorithm = algorithm
                e.save()
                return redirect('resolve_exam', exam_id=exam_id)
        else:
            if max_quantity > 0:
                form = ConfigForm(max_quantity)
                context['form'] = form
                return render(
                    request,
                    'choicemaster/exam/configure_exam3.html',
                    context)
            else:
                message = "Sorry there are not questions about those topics" \
                          "yet! We invite you to suggest some on the Suggest" \
                          " a question section"
                return render(request,
                              'choicemaster/index.html',
                              {'message': message})

    else:
        message = "You have already taken that exam." \
            + " Please create a new one from the 'Take an exam' section"
        return render(request, 'choicemaster/index.html', {'message': message})


def get_first(iterable, default=None):
    if iterable:
        for item in iterable:
            return item
    return default


def resolve_exam(request, exam_id=''):
    """
    View to actually solve the exam. Consider two cases:
    1. request has been sent for the first time on this exam, in which case it
    contains the information about the exam settings (subject, timer, quantity,
    algorithm). Generate an ExamView for such settings, fill the exam object
    with questions and then choose the first question from the first topic in
    order to display it in the resolve_exam template

    2. request method is POST, which means it has been triggered by a solution
    submitted in the front end. Check whether the answer given by the user is
    right or wrong to keep a record to be used in the algorithm to display
    questions afterwards. Also, keep track of remaining time and use it to pass
    to the next question in case it is over.
    :param request: Request, str
    :return: View
    """
    if request.method != 'POST':
        exam = models.Exam.objects.get(pk=exam_id)
        if not exam.closed:
            subject = exam.subject
            timer = exam.exam_timer
            algorithm = exam.exam_algorithm
            topic_ids = exam.topic.all()  # TODO
            mistakes = {}
            # We store all the questions of the selected topics
            for item in topic_ids:
                questions_tmp = models.Question.objects.filter(
                    topic=models.Topic
                    .objects
                    .get(pk=item.id),
                    available=True)
                mistakes[str(item.id)] = 0
                for q in questions_tmp:
                    exam.questions.add(q)

            exam.mistakes = json.dumps(mistakes)
            exam.save()

            # Select a random question for the first one.
            question = get_question(exam_id)

            # Generate the form
            form = ExamForm(question=question.id)

            context = dict()
            context['subject'] = subject
            context['topic'] = question.topic
            context['form'] = form
            context['question'] = question
            context['exam_id'] = exam_id
            context['timer'] = timer
            context['questions_used'] = exam.questions_used.all()
            return render(request, 'choicemaster/exam/resolve_exam.html',
                          context)
        else:
            message = "You have already taken that exam." + \
                " Please create a new one from the 'Take an exam' section"
            return render(request, 'choicemaster/index.html',
                          {'message': message})

    else:
        form = ExamForm(request.POST)
        exam_id = request.POST.get('exam_id')
        exam = models.Exam.objects.get(pk=exam_id)
        if not exam.closed:
            # Check if the exam is not closed
            timer = exam.exam_timer
            question_id = request.POST.get('question_id')
            question = Question.objects.get(pk=question_id)
            answers = Answer.objects.filter(question=question.id)
            correct_answer = answers.filter(correct=True)[0]

            answer_id = request.POST.get('answer')
            if answer_id == '':
                # make up a fake answer which is not the correct one
                answer = get_first(answers.filter(correct=False))
            else:
                # get the actual answer from the front-end if there is one
                answer = Answer.objects.get(pk=answer_id)

            topic_id = question.topic.id
            value = (correct_answer.id == answer.id)
            exam.remaining -= 1
            mistakes = get_mistakes(exam_id)
            if not value:
                mistakes[str(topic_id)] += 1
            else:
                exam.amount_correct += 1

            exam.mistakes = json.dumps(mistakes)
            exam.exam_result = exam.amount_correct / \
                float(exam.exam_quantity_questions)
            exam.save()

            if exam.remaining:
                # Get the next question
                question = get_question(exam_id)
                # Generate the form
                form = ExamForm(question=question.id)

                # Build the context for the next iteration
                context = dict()
                context['exam_id'] = exam_id
                context['form'] = form
                context['question'] = question
                context['questions_used'] = exam.questions_used.all()
                context['timer'] = timer
                context['subject'] = models.Subject.objects.get(
                    pk=exam.subject.id)

                return render(request, 'choicemaster/exam/resolve_exam.html',
                              context)
            else:
                # End of the exam
                exam.exam_result = exam.amount_correct / \
                    float(exam.exam_quantity_questions)
                exam.closed = True

                context = dict()
                context['exam_id'] = exam_id
                context['exam_finished'] = True
                context['passed'] = False
                context['no_questions'] = exam.exam_quantity_questions
                context['no_correct_answers'] = exam.amount_correct
                context['result'] = "{0:.2f}".format(exam.exam_result * 100)

                if exam.exam_result >= exam.passing_score:
                    exam.passed = True
                    context['passed'] = True

                exam.save()
            return render(request, 'choicemaster/index.html', context)
        else:
            message = "You have already taken that exam." +\
                      "Please create a new one from the 'Take an exam' section"

    return render(request, 'choicemaster/index.html', {'message': message})


@login_required
def subjects_statistics(request):
    """
    Get all subjects that the user has been evaluated in, differentiating the
    average grade in that subject, and then display it
    :param request: Request object
    :return: View
    """
    user = request.user
    user_exams_deleteable = models.Exam.objects \
        .filter(user=user,
                exam_quantity_questions=0)
    user_exams_deleteable.delete()
    user_exams = models.Exam.objects.filter(user=user)
    subjects = Subject.objects.all()
    evaluated = dict()
    for s in subjects:
        s_exams = user_exams.filter(subject=s)
        total = s_exams.count()
        if total > 0:
            # There are exams of the subject s.
            partial = 0
            for exam in s_exams:
                partial += exam.exam_result * 10
            # Calculate the final result of the subject s
            result = "{0:.2f}".format(partial / total)
            evaluated[s.id] = (s, result)

    context = dict()
    context['evaluated'] = evaluated
    return render(request, 'choicemaster/statistics/subjects.html', context)


@login_required
def subject_detail(request, subject_id):
    """
    Get general statistics for a determined subject, displaying average grade,
    total questions answered, etc.
    :param request: Request
    :param subject_id: int
    :return: View
    """
    user = request.user
    subject = models.Subject.objects.get(id=subject_id)
    user_exams = models.Exam.objects.filter(user=user, subject=subject)

    subject_title = subject.subject_title
    exams = dict()

    avg = 0
    taken = 0
    questions = 0
    correct = 0
    data = [['Time', 'Result'], ]
    for e in user_exams:
        taken += 1
        exams[e.id] = "Exam " + str(taken)
        avg += e.exam_result
        data.append([taken, e.exam_result * 10])
        questions += e.exam_quantity_questions
        correct += e.amount_correct

    exams_general = (
        "{0:.2f}".format(
            (avg / taken) * 10),
        taken,
        questions,
        correct,
        questions - correct)

    data_source = SimpleDataSource(data=data)
    chart = LineChart(data_source)

    context = dict()
    context['subject_title'] = subject_title
    context['exams_general'] = exams_general
    context['exams'] = exams
    context['chart'] = chart

    return render(request, 'choicemaster/statistics/subject_detail.html',
                  context)


@login_required
def exam_detail(request, exam_id):
    """
    Show data for a determined exam, displaying grade, questions and mistakes
    :param request: Request
    :param exam_id: int
    :return: View
    """
    user = request.user
    e = models.Exam.objects.get(pk=exam_id)

    context = dict()
    context['topics'] = e.topic.all()
    context['result'] = e.exam_result * 10
    context['amount_incorrect'] = e.exam_quantity_questions - e.amount_correct
    context['exam'] = e

    return render(request, 'choicemaster/statistics/exam_detail.html',
                  context)
