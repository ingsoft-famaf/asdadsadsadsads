def question_has_similar(question_text, topic_id):
    """
    Checks if a question is already created in the db. Returns true in that case.
    """
    questions = models.Question.objects.filter(question_text = question_text)
    
    if questions.count() > 0:
        for q in questions:
            if topic_id == q.topic_id:
                return True
    return False


def parse_xml_question(xmlfile, topic_id):
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