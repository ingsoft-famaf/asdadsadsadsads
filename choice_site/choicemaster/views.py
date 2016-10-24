from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from models import Report

@login_required
def index(request):
    return render(request, 'choicemaster/index.html',
                  {"reported": Report.objects.exclude(report_state='E')
                  .count()})
"""
Le paso al template la cantidad de reportes sin ser evaluados que hay en el
momento.
"""