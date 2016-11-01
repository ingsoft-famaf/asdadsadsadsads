from lxml import etree
from io import BytesIO, StringIO
from choicemaster import models
import os


def questions_already_exist(questions_xml, topic_id):
    """
    From a list of questions, checks if any of them is already in the database.
    Returns a dictionary with a key 'status' that is True if exists a similar
    question, a 'question_id' from the question that would be equal and
    a 'topic_id' from the topic the questions are in.
    """
    result = dict()
    result['status'] = True
    result['topic_id'] = topic_id

    questions_db_texts = []
    questions_xml_texts = []

    questions_db = models.Question.objects.filter(topic_id=topic_id)
    # Add all the questions that are already on the database
    for q in questions_db:
        questions_db_texts.append(q.question_text)

    # Add all questions that we want to add, one by one, checking an equal
    # question.
    for q in questions_xml:
        if q.text in questions_db_texts:
            result['in_db'] = True
            result['question_id'] = models.Question.objects.filter(
                question_text=q.text)[0]
            return result
        elif q.text in questions_xml_texts:
            result['in_db'] = False
            return result
        else:
            questions_xml_texts.append(q.text)

    result['status'] = False
    return result


def parse_xml_question(xmlfile, topic_id):
    """
    Parse the xml uploaded by the admin user to create and populate questions
    with their respective answers.
    """
    result = dict()
    result['status'] = True
    result['message'] = 'Questions added succesfully'

    script_dir = os.path.dirname(__file__)

    # Get schema from XSD file to validate XML questions file
    with open(os.path.join(script_dir, 'quiz.xsd'), 'r') as fl_xsd:
        xsd = fl_xsd.read()
        fl_xsd.close()

    # Set a new path called media, joined to script_dir
    media_dir = os.path.join(script_dir, 'media')

    # Use newly created media_dir path in case there was not one previously
    # set
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)

    # Store file received from user in a temporary file 
    with open(os.path.join(media_dir, 'file_tmp.xml'), 'w') as destination:
        for chunk in xmlfile.chunks():
            destination.write(chunk)

    # Copy received file into a variable to operate on it afterwards
    with open(os.path.join(media_dir, 'file_tmp.xml'), 'r') as fl_xml:
        xml = fl_xml.read()
        fl_xml.close()

    # Process XSD
    schema_root = etree.XML(xsd)
    schema = etree.XMLSchema(schema_root)

    # Define XML parser with XSD validation
    parser = etree.XMLParser(schema=schema)
    try:
        for data in xml:
            parser.feed(data)
        root = parser.close()
    except:
        result['status'] = False
        result['message'] = 'Wrong format in uploaded file.'
        return result

    # Create a list with the questions in root as its elements
    questions = root.findall('question')

    # Check if every question already exists in the DB before adding them.
    qae = questions_already_exist(questions, topic_id)
    if qae['status']:
        result['status'] = False
        if qae['in_db']:
            result['message'] = 'Similar question already present in' \
                                'database.'
            result['topic_id'] = qae['topic_id']
            result['question_id'] = qae['question_id']
        else:
            result['message'] = 'Similar question already being added in ' \
                                'xml file'

        return result

    # After checking that all the questions are new, add them to the DB.
    for item in questions:
        question = models.Question()
        question.question_text = item.text
        question.topic_id = topic_id
        question.save()
        item_children = item.getchildren()
        for children in item_children:
            answer = models.Answer()
            answer.answer_text = children.text
            if children.tag == 'corrrect':
                answer.correct = True
            else:
                answer.correct = False
            answer.question_id = question.id
            answer.save()
            
    return result