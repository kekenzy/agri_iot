from django import forms

class FamilyInfo(forms.Form):
    name = forms.CharField(
        label='名字',
        widget=forms.TextInput(attrs={'class': 'name-class'})
    )

    # def __init__(self, *args, **kwargs):
    #     super(FamilyInfo, self).__init__(self, *args, **kwargs)
        # self.fields['job'].widget.attrs['id'] = 'id_job'
        # self.fields['job'].widget.attrs['class'] = 'hobbies_class'