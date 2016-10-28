from django.forms import Form, ModelForm, FileField
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