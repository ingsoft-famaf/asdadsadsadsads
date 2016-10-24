from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from lxml import etree
from StringIO import StringIO


@login_required
def index(request):
    return render(request, 'choicemaster/index.html')


def parseQuestionXML(xmlFile):
    """
    Parse the xml
    """
    f = open(xmlFile)
    xml = f.read()
    f.close()
 
    tree = etree.parse(StringIO(xml))
    context = etree.iterparse(StringIO(xml))
    question = {}
    questions_list = []
    for action, elem in context:
        if not elem.text:
            text = "None"
        else:
            text = elem.text
        print elem.tag + " => " + text
        question[elem.tag] = text
        if elem.tag == "book":
            questions_list.append(question)
            question = {}
    return questions_list

if __name__ == "__main__":
    parseBookXML("/choicemaster/questionSample.xml")