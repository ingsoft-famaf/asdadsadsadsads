import sys
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from models import Topic, Answer, Question, Report
import json



@csrf_exempt
def suggestion(request):

    if request.method == 'POST' and request.is_ajax:
        """ Parseo la lista """
        list = request.POST.get("list")
        list = list[1:-1]
        list = list.split(",")

        correct = request.POST.get("correct")
        question = request.POST.get("question")
        topic_id = request.POST.get('topic')
        topic = Topic.objects.get(pk=topic_id)
        quest = Question.objects.create(question_text=question,topic=topic,
                                        available=False)
        for i, val in enumerate(list):
            list[i] = list[i][1:-1]
            if correct == i:
                Answer.objects.create(answer_text= list[i], question=quest,
                                      correct=True)
            else:
                Answer.objects.create(answer_text= list[i], question=quest,
                                      correct=False)
        return HttpResponse("OK")
    else:
        return HttpResponse("Something went wrong")


@csrf_exempt
def add_report(request):
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
       Cambia el estado de un reporte a evaluado, lo elimina de los reportes
        pendientes.
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
        Elimina la pregunta y todas sus respuestas asociadas, asi tambien
        elimina el reporte (no cambia el estado) ya que pierde la relacion
        con question.
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
        Elimina una respuesta.
    """
    if request.is_ajax() and request.POST:
        Answer.objects.get(id=request.POST.get('idA')).delete()
        return HttpResponse("Deleted")
    else:
        return HttpResponse("Not deleted")


@csrf_exempt
def edit_question(request):
    """
        Cambia la pregunta. Se pide que ingrese la nueva pregunta y se la
        remplaza, ademas cambia el estado del reporte por evaluated.
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
        Cambia la opcion correcta de la pregunta.
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
        Cambia una repuesta y actualiza el estado del reporte.
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
    Aceptar una sugerencia de un usuario
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
