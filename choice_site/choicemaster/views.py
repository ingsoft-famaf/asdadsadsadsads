from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from models import Report

@login_required
def index(request):
    return render(request, 'choicemaster/index.html',{"reported":
                                                          Report.objects.count()})
