import sys
from django.shortcuts import HttpResponse, redirect
from django.views.decorators.csrf import csrf_exempt
from models import Topic, Answer, Question, Report
import json
from . import upload


@csrf_exempt
def get_quantity_suggestions(request):
    """
    Gets the quantity of suggestions and returns just that
    :param request: Request
    :return: HttpResponse
    """
    if request.method == 'POST' and request.is_ajax:
        suggestions = Question.objects.filter(available=False)
        data = str(len(suggestions))
        return HttpResponse(data)


@csrf_exempt
def suggestion(request):
    """
    Generates a question with its associated choices from the suggestion
    received from the user
    :param request: Request
    :return: HttpResponse
    """
    if request.method == 'POST' and request.is_ajax:
        lst = json.loads(request.POST.get('lst'))

        correct = int(request.POST.get('correct'))
        question = request.POST.get('question').strip()
        topic_id = request.POST.get('topic')

        result = upload.questions_already_exist([question], topic_id)
        if result['status']:
            data = {'status': True}
            return HttpResponse(json.dumps(data),
                                content_type='application/json')
        else:
            topic = Topic.objects.get(pk=topic_id)
            quest = Question.objects.create(
                question_text=question, topic=topic, available=False)

            lst_len = len(lst)
            for i in range(lst_len):
                el = lst[i]
                if correct == i:
                    Answer.objects.create(answer_text=el, question=quest,
                                          correct=True)
                else:
                    Answer.objects.create(answer_text=el, question=quest,
                                          correct=False)
            data = {'status': False}
            return HttpResponse(json.dumps(data),
                                content_type='application/json')
    else:
        return HttpResponse("Something went wrong")


@csrf_exempt
def add_report(request):
    """
    Adds a report filled by a user to the site's reports record
    :param request: Request
    :return: HttpResponse
    """
    if request.method == 'POST' and request.is_ajax:
        deq = request.POST.get('description')
        idq = request.POST.get('idq')
        quest = Question.objects.get(id=idq)
        report = Report(report_description=deq)
        report.question = quest
        report.save()
        return HttpResponse("OK")
    else:
        return HttpResponse("Something went wrong")


@csrf_exempt
def ajax_view(request):
    """
    Shows the topics associated to a given subject
    :param request: Request
    :return: HttpResponse
    """
    if request.method == 'POST' and request.is_ajax:
        topics = Topic.objects.all().filter(subject_id=request.POST.get('ids'))
        innerHTML = ''
        template = '<option value='
        for t in topics:
            id = str(t.id)
            title = t.topic_title
            innerHTML += template + '"' + id + '">' + title + '</option>\n'
        data = {'topics': innerHTML}
        return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        return HttpResponse("Something went wrong")


@csrf_exempt
def get_correct(request):
    """
    Gets the correct answer to a given question
    :param request: Request
    :return: HttpResponse
    """
    if request.method == 'POST' and request.is_ajax:
        question_id = request.POST.get('idq')
        chosen = request.POST.get('chosen')
        question = Question.objects.get(pk=question_id)
        answers = Answer.objects.filter(question=question.id)
        correct_answer = answers.filter(correct=True)
        data = {'answer': correct_answer[0].answer_text,
                'equal': correct_answer[0].answer_text == chosen[1:]}
        return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        return HttpResponse("Something went wrong")


@csrf_exempt
def autoreport(request):
    """
    Generates a report automatically for a denounced question as repeated in
    an exam
    :param request: Request
    :return: HttpResponse
    """
    if request.method == 'POST' and request.is_ajax:
        txt = Question.objects.get(id=request.POST.get('id1')).question_text
        deq = "Esta pregunta esta duplicada con la pregunta con \"" + txt + \
              "\""
        idq = request.POST.get('id2')
        quest = Question.objects.get(id=idq)
        report = Report(report_description=deq)
        report.question = quest
        report.save()
        return HttpResponse("OK")
    else:
        return HttpResponse("Something went wrong")


@csrf_exempt
def delete_report(request):
    """
    Changes the state of an evaluated report, removes it from the list of
    pending reports.
    :param request: Request
    :return: HttpResponse
    """
    if request.is_ajax() and request.POST:
        report = Report.objects.get(id=request.POST.get('id'))
        report.report_state = Report.EVALUATED
        report.save()
        return HttpResponse("Deleted")
    else:
        return HttpResponse("Not deleted")


@csrf_exempt
def delete_question(request):
    """
    Eliminates the question and all its associated answers, just like the
    report that denounced the question (it does not change its state) given
    that it loses its link with the question.
    :param request: Request
    :return: HttpResponse
    """
    if request.is_ajax() and request.POST:
        question = Question.objects.get(id=request.POST.get('idQ'))
        question.delete()
        return HttpResponse("Deleted")
    else:
        return HttpResponse("No deleted")


@csrf_exempt
def delete_answer(request):
    """
    Removes an answer from a question.
    :param request: Request
    :return: HttpResponse
    """
    if request.is_ajax() and request.POST:
        Answer.objects.get(id=request.POST.get('idA')).delete()
        return HttpResponse("Deleted")
    else:
        return HttpResponse("Not deleted")


@csrf_exempt
def edit_question(request):
    """
    Changes the question. It asks to enter the new question and replaces it,
    also changes the report state to 'evaluated'
    :param request: Request
    :return: HttpResponse
    """
    if request.is_ajax() and request.POST:
        question = Question.objects.get(id=request.POST.get('id'))
        new_value = request.POST.get('newValue')
        question.question_text = new_value
        question.save()
        return HttpResponse("Deleted")
    else:
        return HttpResponse("Not deleted")


@csrf_exempt
def edit_correct(request):
    """
    Changes the correct choice of a question to another one.
    :param request: Request
    :return: HttpResponse
    """
    if request.is_ajax() and request.POST:
        # Busco la respuesta correta de la pregunta con id = idQ
        question = Question.objects.get(id=request.POST.get('idQ'))
        answers = Answer.objects.filter(question=question.id)
        answers = answers.filter(correct=True)
        correct_answer = answers[0]
        correct_answer.correct = False
        # La marco como incorrecta
        correct_answer.save()
        # A la nueva resuesta la pongo como correcta
        answer = Answer.objects.get(id=request.POST.get('idA'))
        answer.correct = True
        answer.save()
        return HttpResponse("Changed")
    else:
        return HttpResponse("Not Changed")


@csrf_exempt
def edit_ans(request):
    """
    Changes an answer and updates the report state.
    :param request: Request
    :return: HttpResponse
    """
    if request.is_ajax() and request.POST:
        ans = Answer.objects.get(id=request.POST.get('id'))
        new_value = request.POST.get('newValue')
        ans.answer_text = new_value
        ans.save()
        return HttpResponse("Deleted")
    else:
        return HttpResponse("No deleted")


@csrf_exempt
def accept_suggestion(request):
    """
    Accepts a suggestion from a user.
    :param request: Request
    :return: HttpResponse
    """
    if request.is_ajax() and request.POST:
        question = Question.objects.get(id=request.POST.get('idQ'))
        question.available = True
        question.save()
        return HttpResponse("Added suggestion")
    else:
        return HttpResponse("Error!")
