from django.forms import Form, ModelForm, FileField, DecimalField
from django import forms
from .models import Subject, Topic, Question, Answer, QuestionSnapshot
from django.core.validators import MinValueValidator, MaxValueValidator


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


class SubjectForm(forms.Form):
    subject = forms.ChoiceField(choices=get_subjects(), widget=forms.Select(attrs={'onchange': 'form.submit();'}))


class MultipleTopicForm(forms.Form):
    topic = forms.MultipleChoiceField(choices=get_subjects(),
                                        widget=forms.CheckboxSelectMultiple)

    def __init__(self, ids, *args, **kwargs):
        super(MultipleTopicForm, self).__init__(*args, **kwargs)
        self.fields['topic'].choices = get_topics(ids)


ALGORITHMS = (('0', 'Based on errors'), ('1', 'Random'))


class ConfigForm(forms.Form):
    quantity = forms.IntegerField(label="Quantity of questions to solve:")
    timer = forms.IntegerField(validators=[MinValueValidator(5),
                                       MaxValueValidator(120)],
                                help_text="Input in seconds",
                                label="Write the amount of time per question required:")
    algorithm = forms.ChoiceField(choices=ALGORITHMS, label="Choose an algorithm:")

    def __init__(self, max_quantity, *args, **kwargs):
        super(ConfigForm, self).__init__(*args, **kwargs)
        self.fields['quantity'].validators =\
            [MaxValueValidator(max_quantity)]


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

    def __init__ (self, *args, **kwargs):
        question_id = None
        if kwargs:
            question_id = kwargs.pop('question')
        super(ExamForm, self).__init__(*args, **kwargs)
        if question_id:
            self.fields['answer'].queryset = Answer.objects.filter(question=question_id)
        else:
            self.fields['answer'].queryset = Answer.objects.filter(question=0)


TOPICS = (('0', 'Select Topic'), ('1', '---'))


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
