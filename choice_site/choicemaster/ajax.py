from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from models import Topic
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
        return HttpResponse("Something went wrong in ajax_view")