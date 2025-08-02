from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from agri_app.models import UserProfile

class ProfileEditForm(forms.ModelForm):
    """プロフィール編集フォーム"""
    first_name = forms.CharField(
        label='氏名',
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    email = forms.EmailField(
        label='メールアドレス',
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-input'})
    )

    class Meta:
        model = User
        fields = ('first_name', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
        }

class ProfilePasswordChangeForm(PasswordChangeForm):
    """パスワード変更フォーム"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].label = '現在のパスワード'
        self.fields['new_password1'].label = '新しいパスワード'
        self.fields['new_password2'].label = '新しいパスワード（確認）'
        
        self.fields['old_password'].widget.attrs.update({'class': 'form-input'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-input'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-input'}) 