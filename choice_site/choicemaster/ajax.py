from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Report, Question, Answer


from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from models import Topic, Answer, Question, Report
import json


@csrf_exempt
def ajax_view(request):
    if request.method == 'POST' and request.is_ajax:
        topics = Topic.objects.all().filter(subject_id=request.POST.get('ids'))
        lt = []
        for t in topics:
            lt.append((str(t.id), t.topic_title))
        data = {'topics': lt}
        return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        return HttpResponse("Something went wrong")


@csrf_exempt
def get_correct(request):
    if request.method == 'POST' and request.is_ajax:
        question_id = request.POST.get('idq')
        question = Question.objects.get(pk=question_id)
        answers = Answer.objects.filter(question=question.id)
        correct_answer = answers.filter(correct=True)
        data = {'answer': correct_answer[0].answer_text}
        return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        return HttpResponse("Something went wrong")

@csrf_exempt
def autoreport(request):
    if request.method == 'POST' and request.is_ajax:
        question = Question.objects.get(id=request.POST.get('id2'))
        id = request.POST.get('id1')
        Report.objects.create(question=question,
                              report_description="Esta pregunta esta "
                                                 "duplicada con la pregunta "
                                                 + str(id))

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
        return HttpResponse("Delted")
    else:
        return HttpResponse("No deleted")


@csrf_exempt
def delete_question(request):
    """
        Elimina la pregunta y todas sus respuestas asociadas, asi tambien elimina
         el reporte (no cambia el estado) ya que pierde la relacion con question.
    """
    if request.is_ajax() and request.POST:
        question = Question.objects.get(id=request.POST.get('idQ'))
        question.delete()
        return HttpResponse("Delted")
    else:
        return HttpResponse("No deleted")


@csrf_exempt
def delete_answer(request):
    """
        Elimina una respuesta.
    """
    if request.is_ajax() and request.POST:
        report = Report.objects.get(id=request.POST.get('idR'))
        report.report_state = Report.EVALUATED
        report.save()

        Answer.objects.get(id=request.POST.get('idA')).delete()
        return HttpResponse("Delted")
    else:
        return HttpResponse("No deleted")


@csrf_exempt
def edit_question(request):
    """
        Cambia la pregunta. Se pide que ingrese la nueva pregunta y se la remplaza,
        ademas cambia el estado del reporte por evaluated.
    """
    if request.is_ajax() and request.POST:
        question = Question.objects.get(id=request.POST.get('id'))
        new_value = request.POST.get('newValue')
        question.question_text = new_value
        question.save()

        report = Report.objects.get(id=request.POST.get('idR'))
        report.report_state = Report.EVALUATED
        report.save()
        return HttpResponse("Delted")
    else:
        return HttpResponse("No deleted")


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

        report = Report.objects.get(id=request.POST.get('idR'))
        report.report_state = Report.EVALUATED
        report.save()
        return HttpResponse("Delted")
    else:
        return HttpResponse("No deleted")
