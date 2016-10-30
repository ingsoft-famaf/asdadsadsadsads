from django import forms


class UploadQuestionFileForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file',
    )