from lxml import etree
from io import BytesIO, StringIO
from choicemaster import models
import os

def question_has_similar(question_text, topic_id):
    """
    Checks if a question is already created in the db. Returns true in that case.
    """
    questions = models.Question.objects.filter(question_text = question_text, topic = topic_id)
    
    if questions.count():
        return True
    return False


def parse_xml_question(xmlfile, topic_id):
    """
    Parse the xml uploaded by the admin to create and populate questions with their answers
    """
    script_dir = os.path.dirname(__file__)

    fl_xsd = open(os.path.join(script_dir, 'quiz.xsd'), 'r')
    xsd = fl_xsd.read()
    fl_xsd.close()

    with open(os.path.join(script_dir, 'media/file_tmp.xml'), 'w') as destination:
        for chunk in xmlfile.chunks():
            destination.write(chunk)

    fl_xml = open(os.path.join(script_dir, 'media/file_tmp.xml'), 'r')
    xml = fl_xml.read()
    fl_xml.close()


    schema_root = etree.XML(xsd)
    schema = etree.XMLSchema(schema_root)
    etree.XMLParser(schema=schema)

    parser = etree.XMLParser(dtd_validation=True)
    for data in StringIO(xml):
        parser.feed(data)
    root = parser.close()

    questions = root.findall('question')

    for item in questions:
        """
        Check if every question already exists in the DB before adding them.
        """
        if question_has_similar(item.text, topic_id):
            return False

    """
    After checking all the questions are new, we add them to the DB.
    """
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
    return True