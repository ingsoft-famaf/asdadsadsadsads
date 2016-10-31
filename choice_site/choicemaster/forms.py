from django import forms
from models import Subject, Topic

def get_subjects():
    subjects = Subject.objects.all()
    choices = dict()
    for s in subjects:
        choices[str(s.id)] = s.subject_title
    choices['0'] = 'None'
    choices = choices.items()
    choices.sort()
    return choices


def get_topics(subject_id=0):
    topics = Topic.objects.all().filter(subject_id=subject_id)
    choices = dict()
    for s in topics:
        choices[str(s.id)] = s.topic_title
    choices['0'] = 'None'
    choices = choices.items()
    choices.sort()
    return choices

TOPICS = (('0', 'None'), ('1', '---'))


class UploadQuestionForm(forms.Form):
    subject = forms.ChoiceField(choices=get_subjects(), widget=forms.Select(
                                          attrs={'onchange': "get_topics()"}))
    topic = forms.ChoiceField(choices=TOPICS)
    xmlfile = forms.FileField(label='Choose XML file')


# class TopicsForm(forms.Form):
#    topic_field = forms.ChoiceField(choices=TOPICS, widget=forms.Select(
#        attrs={'onchange': "this.form.submit();"}))


class UploadQuestionFileForm(forms.Form):
    docfile = forms.FileField(label='Select a file')