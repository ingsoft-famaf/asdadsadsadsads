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


@login_required
@staff_member_required
def add_question_w_subject(request, subject_id):
    subject = models.Subject.objects.filter(id=subject_id)[0]
    topics = models.Topic.objects.filter(subject_id=subject_id)
    context = dict()
    context['subject'] = subject
    context['topics'] = topics
    return render(request, 'choicemaster/add/question/w_subject.html', context)


@login_required
@staff_member_required
def add_question_w_subject_topic(request, subject_id, topic_id):
    subject = models.Subject.objects.filter(id=subject_id)[0]
    topic = models.Topic.objects.filter(id=topic_id)[0]
    context = dict()
    context['subject'] = subject
    context['topic'] = topic
    return render(request, 'choicemaster/add/question/w_subject_topic.html', context)


def question_has_similar(question):
    # TODO real implementation
    return False


def parse_question(xmlfile, topic_id):
    """
    Parse the xml uploaded by the admin to create and populate questions with their answers
    """
    fl = open(xmlfile, 'r')
    xml = fl.read()
    fl.close()

    fl = open('/quiz.xsd', 'r')
    xsd = fl.read()
    fl.close()

    schema_root = etree.XML("'''" + xsd + "'''")
    schema = etree.XMLSchema(schema_root)
    etree.XMLParser(schema=schema)

    parser = etree.XMLParser(dtd_validation=True)
    for data in StringIO(xml):
        parser.feed(data)
    root = parser.close()

    questions = root.findall('question')

    for item in questions:
        question = models.Question()
        question.question_text = item.text

        if question_has_similar(question):
            # TODO redirect to upload again with message to change the title.
            pass
        else:
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
                # TODO redirect to success message
