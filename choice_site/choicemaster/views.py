from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from lxml import etree
from StringIO import StringIO


@login_required
def index(request):
    return render(request, 'choicemaster/index.html')


def parseXML(xmlFile):
    """
    Parse the xml
    """
    f = open(xmlFile)
    xml = f.read()
    f.close()
 
    tree = etree.parse(StringIO(xml))
    # e.g. tree = etree.parse("/choicemaster/questionSample.xml")
    context = etree.iterparse(StringIO(xml))
    for action, elem in context:
        if not elem.text:
            text = "None"
        else:
            text = elem.text
        print elem.tag + " => " + text