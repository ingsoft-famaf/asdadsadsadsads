from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Report, Question, Answer

"""
   Cambia el estado de un reporte a evaluado, lo elimina de los reportes
    pendientes.
"""


@csrf_exempt
def delete_report(request):
    if request.is_ajax() and request.POST:
        report = Report.objects.get(id=request.POST.get('id'))
        report.report_state = Report.EVALUATED
        report.save()
        return HttpResponse("Delted")
    else:
        return HttpResponse("No deleted")


"""
    Elimina la pregunta y todas sus respuestas asociadas, asi tambien elimina
     el reporte (no cambia el estado) ya que pierde la relacion con question.
"""


@csrf_exempt
def delete_question(request):
    if request.is_ajax() and request.POST:
        question = Question.objects.get(id=request.POST.get('idQ'))
        question.delete()
        return HttpResponse("Delted")
    else:
        return HttpResponse("No deleted")


"""
    Elimina una respuesta.
"""


@csrf_exempt
def delete_answer(request):
    if request.is_ajax() and request.POST:
        report = Report.objects.get(id=request.POST.get('idR'))
        report.report_state = Report.EVALUATED
        report.save()

        Answer.objects.get(id=request.POST.get('idA')).delete()
        return HttpResponse("Delted")
    else:
        return HttpResponse("No deleted")


"""
    Cambia la pregunta. Se pide que ingrese la nueva pregunta y se la remplaza,
    ademas cambia el estado del reporte por evaluated.
"""


@csrf_exempt
def edit_question(request):
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


"""
    Cambia una repuesta y actualiza el estado del reporte.
"""


@csrf_exempt
def edit_ans(request):
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
