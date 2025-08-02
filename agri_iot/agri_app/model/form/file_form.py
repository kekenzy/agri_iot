# agri_app/model/form/file_form.py

from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField(label='ファイルを選択')
