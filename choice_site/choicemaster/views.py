from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from lxml import etree


@login_required
def index(request):
    return render(request, 'choicemaster/index.html')

tree = etree.parse("/choicemaster/questionSample.xml")

for user in tree.xpath("/choicemaster/questionSample.xml"):
    print(user.text)