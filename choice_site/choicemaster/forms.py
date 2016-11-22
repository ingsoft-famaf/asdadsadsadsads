from django import forms
from .models import Subject, Topic, Answer
from django.core.validators import MinValueValidator, MaxValueValidator

import customWidget


def get_topics(ids):
    topics = Topic.objects.filter(subject_id=ids)
    choices = dict()
    for t in topics:
        choices[str(t.id)] = t.topic_title
    choices = sorted(choices.items())
    return choices


class SubjectForm(forms.ModelForm):
    subject = forms.ModelChoiceField(queryset=Subject.objects.all(),
                                widget=forms.Select(attrs={'onchange':
                                                           'form.submit();'}))

    class Meta:
        model = Subject
        exclude = ['subject_title', 'subject_description', 'subject_department']


class MultipleTopicForm(forms.ModelForm):
    topic = forms.ModelMultipleChoiceField(
        queryset=Topic.objects.all(),
        required=False,
        widget=customWidget.CheckboxSelectMultiple)

    def __init__(self, ids, *args, **kwargs):
        super(MultipleTopicForm, self).__init__(*args, **kwargs)
        self.fields['topic'].queryset = Topic.objects.filter(subject_id=ids)

    class Meta:
        model = Topic
        exclude = ['subject', 'topic_title', 'topic_description']


ALGORITHMS = (('0', 'Based on errors'), ('1', 'Random'))


class ConfigForm(forms.Form):
    quantity = forms.IntegerField(label="Quantity of questions to solve:")
    timer = forms.IntegerField(validators=[MinValueValidator(5),
                                           MaxValueValidator(120)],
                               help_text="Input in seconds",
                               label="Write the amount of time per question "
                                     "required:")
    algorithm = forms.ChoiceField(choices=ALGORITHMS, label="Choose an "
                                                            "algorithm:")

    def __init__(self, max_quantity, *args, **kwargs):
        super(ConfigForm, self).__init__(*args, **kwargs)
        self.fields['quantity'].validators =\
            [MaxValueValidator(max_quantity)]


class ExamForm(forms.ModelForm):

    answer = forms.ModelChoiceField(required=True, widget=forms.RadioSelect,
                                    queryset=Answer.objects.all())

    class Meta:
        model = Answer
        exclude = ['question', 'correct']

    def __init__(self, *args, **kwargs):
        question_id = None
        if kwargs:
            question_id = kwargs.pop('question')
        super(ExamForm, self).__init__(*args, **kwargs)
        if question_id:
            self.fields['answer'].queryset = Answer.objects.filter(
                question=question_id)
        else:
            self.fields['answer'].queryset = Answer.objects.filter(question=0)


TOPICS = (('0', 'Select Topic'), ('1', '---'))


class UploadQuestionForm(forms.Form):
    subject = forms.ModelChoiceField(required=True,
                                     widget=forms.Select(attrs={'onchange':
                                                                'get_topics('
                                                                ');'}),
                                     queryset=Subject.objects.all())
    topic = forms.ChoiceField(choices=TOPICS)
    xmlfile = forms.FileField(label='Choose XML file')