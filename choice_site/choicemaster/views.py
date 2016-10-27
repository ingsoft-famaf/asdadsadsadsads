from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def index(request, message=''):
    if message:
        context = {'message': message}
    else:
        context = {'message': 'Everything ok!'}
    return render(request, 'choicemaster/index.html', context)
