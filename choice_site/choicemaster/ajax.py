from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from models import Report, Question

@csrf_exempt
def delete_report(request):
    if request.is_ajax() and request.POST:
        report = Report.objects.get(id=request.POST.get('id'))
        report.report_state = Report.EVALUATED
        report.save()
        return HttpResponse("Delted")
    else:
        return  HttpResponse("No deleted")

@csrf_exempt
def delete_question(request):
    if request.is_ajax() and request.POST:
        report = Report.objects.get(id=request.POST.get('idR'))
        report.report_state = Report.EVALUATED
        report.save()

        question = Question.objects.get(id=request.POST.get('idQ'))
        question.delete()