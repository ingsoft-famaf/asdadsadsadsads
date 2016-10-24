from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from lxml import etree
from StringIO import StringIO
from choicemaster import models


@login_required
def index(request):
    return render(request, 'choicemaster/index.html')


@login_required
@staff_member_required
def add_question(request):
    context = dict()
    context['subjects'] = models.Subject.objects.all()
    return render(request, 'choicemaster/add/question.html', context)


def parseQuestionXML(xmlfile, topic_id):
    """
    Parse the xml uploaded by the admin to create and populate questions with their answers
    """
    file = open(xmlfile)
    xml = file.read()
    file.close()

    parser = etree.XMLParser()
    for data in StringIO(xml):
        parser.feed(data)
    root = parser.close()

    questions = root.findall('question')

    for item in questions:
        question = models.Question()
        question.question_text = item.text
        question.topic_id = topic_id
        question.save()
        item_children = item.getchildren
        for children in item_children:
            answer = models.Answer()
            answer.answer_text = children.text
            if children.tag == 'corrrect':
                answer.corrrect = True
            else:
                answer.correct = False
            answer.question_id = question.id
            answer.save()
