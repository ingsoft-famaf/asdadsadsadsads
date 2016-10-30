from django.forms import Form, ModelForm, FileField, DecimalField
from .models import Subject, Topic
from ajax_select import make_ajax_field
from ajax_select.fields import AutoCompleteSelectField, AutoCompleteSelectMultipleField


class UploadFileForm(Form):
    docfile = FileField(
        label='Select a file',
        help_text='max. 42 megabytes'
    )


class ConfigureExamForm(ModelForm):

    subject = make_ajax_field(Subject, 'subject_title', 'subject', help_text="Write a subject", show_help_text=True, label='Select a subject')

    class Meta:
        model = Subject
        exclude = []

class ConfigureForm(Form):
    timer = DecimalField(
        label = 'Time for each question',
        help_text = 'In minutes',
        max_value = 60,
        min_value = 0,
        )
    quantity = DecimalField(
        label = 'Amount of questions',
        # max_value = 60, Deberia ser la cantidad de preguntas para los temas elegidos.
        min_value = 0,
        )