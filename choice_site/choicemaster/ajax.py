from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from models import Topic, Answer
import json

@csrf_exempt
def get_checkboxes(request):
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
        answer = Answer.objects.get(pk=question_id)
        data = {'answer': answer.answer_text}
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
