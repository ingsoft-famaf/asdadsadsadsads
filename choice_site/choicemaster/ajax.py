from django.views.decorators.csrf import csrf_exempt
from models import Report

@csrf_exempt
def delete_report(request):
    if request.is_ajax() and request.POST:
        report = Report.objects.get(id=request.POST.get('id'))
        report.report_state = Report.EVALUATED
        report.save()
