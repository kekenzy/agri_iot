from django import forms

class UserInfo(forms.Form):
    first_name = forms.CharField(
        label='名前',
        widget=forms.TextInput(attrs={'class': 'name-class'})
    )
    email = forms.EmailField()

    # def clean_last_name(self):
    #     last_name = self.clean_data['last_name']
        # if not 
        #     raise forms.ValidationError('エラー')