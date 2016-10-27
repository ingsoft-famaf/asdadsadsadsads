from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from models import Report


@login_required
def index(request, message=''):

    return render(request, 'choicemaster/index.html', context)

def index(request, message=''):
    if message:
        context = {'message': message}
    else:
        context = {'message': 'Everything ok!'}
    context['reported'] = Report.objects.exclude(report_state='E').count()

    return render(request, 'choicemaster/index.html', context)


def report(request):
    """
    Le paso al template la cantidad de reportes sin ser evaluados que hay en el
    momento.
    """
    context = dict()
    context['reports'] = Report.objects.all()
    return render(request, 'choicemaster/report.html', context)
