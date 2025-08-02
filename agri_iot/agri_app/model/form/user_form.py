from django import forms
from django.contrib.auth.models import User

class UserSearchForm(forms.Form):
    username = forms.CharField(
        label='ユーザー名',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'ユーザー名で検索'
        })
    )
    first_name = forms.CharField(
        label='氏名',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '氏名で検索'
        })
    )
    role = forms.ChoiceField(
        label='権限',
        required=False,
        choices=[
            ('', 'すべて'),
            ('superuser', 'スーパーユーザー'),
            ('staff', '管理者'),
            ('user', '一般')
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff', 'is_superuser']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'ユーザー名を入力'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '名を入力'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '姓を入力'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'メールアドレスを入力'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
            'is_staff': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
            'is_superuser': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            })
        }



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