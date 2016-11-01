from django.forms import Form, ModelForm, FileField, DecimalField
from django import forms
from .models import Subject, Topic, Question, Answer
import ipdb

# Ignacio

def get_subjects():
    subjects = Subject.objects.all()
    choices = dict()
    for s in subjects:
        choices[str(s.id)] = s.subject_title
    choices['0'] = 'None'
    choices = choices.items()
    choices.sort()
    return choices

def get_topics(ids):
    topics = Topic.objects.filter(subject_id=ids)
    choices = dict()
    for t in topics:
        choices[str(t.id)] = t.topic_title
    choices = choices.items()
    choices.sort()
    return choices

class ConfigureExamForm2(forms.Form):
    subject = forms.ChoiceField(choices=get_subjects(), widget=forms.Select(
        attrs={'onchange': "get_topics()"}))
    mult_topics = forms.MultipleChoiceField(choices=(),
        widget=forms.CheckboxSelectMultiple)
    timer = forms.DecimalField(
        label = 'Time for each question',
        help_text = 'In minutes',
        max_value = 60,
        min_value = 0)
    quantity = DecimalField(
        label = 'Amount of questions',
        # max_value = 60, Deberia ser la cantidad de preguntas para los temas elegidos.
        min_value = 1)


class SubjectForm(forms.Form):
    subject = forms.ChoiceField(choices=get_subjects(), widget=forms.Select(attrs={'onchange': 'form.submit();'}))


class MultipleTopicForm(forms.Form):
    topic = forms.MultipleChoiceField(choices=get_subjects(),
                                        widget=forms.CheckboxSelectMultiple)

    def __init__(self, ids, *args, **kwargs):
        super(MultipleTopicForm, self).__init__(*args, **kwargs)
        self.fields['topic'].choices = get_topics(ids)


class ConfigForm(forms.Form):
    quantity = forms.IntegerField()
    timer = forms.IntegerField()

# Ignacio

class UploadFileForm(Form):
    docfile = FileField(
        label='Select a file',
        help_text='max. 42 megabytes'
    )


class ExamForm(ModelForm):
    
    answer = forms.ModelChoiceField(required=True, widget=forms.RadioSelect, queryset=Answer.objects.all())

    class Meta:
        model = Answer
        exclude = ['question', 'correct']

    def __init__ (self, question=''):
        question_id = question
        super(ExamForm, self).__init__()
        if question_id:
                self.fields['answer'].queryset = Answer.objects.filter(question=question_id)
