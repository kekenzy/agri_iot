from django import forms
from django.contrib.auth.models import User
from agri_app.models import UserProfile

class UserForm(forms.ModelForm):
    username = forms.CharField(
        label='名前',
        widget=forms.TextInput(attrs={'class': 'name-class'})
    )
    email = forms.EmailField(
        label='メールアドレス',
    )
    password = forms.CharField(
        label='パスワード',
        widget=forms.PasswordInput(),
    )
    confirm_password = forms.CharField(
        label='パスワード再入力',
        widget=forms.PasswordInput(),
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data['password']
        confirm_password = cleaned_data['confirm_password']
        if password != confirm_password:
            raise forms.ValidationError('パスワードが一致しません')

    class Meta():
        model = User
        fields = ('username', 'email', 'password')

    # def clean_last_name(self):
    #     last_name = self.clean_data['last_name']
        # if not 
        #     raise forms.ValidationError('エラー')

class UserProfileForm(forms.ModelForm):
    picture = forms.FileField(
        label='写真',
    )
    family = forms.CharField(
        label='名字',
        widget=forms.TextInput(attrs={'class': 'name-class'})
    )
    class Meta():
        model = UserProfile
        fields = ('picture',)

class LoginForm(forms.Form):
    username = forms.CharField(
        label='ユーザー名またはメールアドレス',
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'name-class', 'placeholder': 'ユーザー名またはメールアドレスを入力'})
    )
    password = forms.CharField(
        label='パスワード',
        widget=forms.PasswordInput(),
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data['password']
        # confirm_password = cleaned_data['confirm_password']
        # if password != confirm_password:
        #     raise forms.ValidationError('パスワードが一致しません')