from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Report, Question, Answer


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
        question = Question.objects.get(id=request.POST.get('idQ'))
        question.delete()
        return HttpResponse("Delted")
    else:
        return HttpResponse("No deleted")

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

@csrf_exempt
def edit_question(request):
    if request.is_ajax() and request.POST:
        question = Question.objects.get(id=request.POST.get('id'))
        new_value =  request.POST.get('newValue')
        question.question_text = new_value;
        question.save()

        report = Report.objects.get(id=request.POST.get('idR'))
        report.report_state = Report.EVALUATED
        report.save()
        return HttpResponse("Delted")
    else:
        return  HttpResponse("No deleted")


@csrf_exempt
def edit_ans(request):
    if request.is_ajax() and request.POST:
        ans = Answer.objects.get(id=request.POST.get('id'))
        new_value =  request.POST.get('newValue')
        ans.answer_text = new_value;
        ans.save()

        report = Report.objects.get(id=request.POST.get('idR'))
        report.report_state = Report.EVALUATED
        report.save()
        return HttpResponse("Delted")
    else:
        return  HttpResponse("No deleted")