from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from agri_app.models import UserProfile

class UserCreateForm(UserCreationForm):
    """ユーザー作成フォーム"""
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
    is_staff = forms.BooleanField(
        label='管理者権限',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )
    is_superuser = forms.BooleanField(
        label='スーパーユーザー権限',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email', 'password1', 'password2', 'is_staff', 'is_superuser')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'ユーザー名'
        self.fields['password1'].label = 'パスワード'
        self.fields['password2'].label = 'パスワード（確認）'
        self.fields['password1'].widget.attrs.update({'class': 'form-input'})
        self.fields['password2'].widget.attrs.update({'class': 'form-input'})

class UserEditForm(forms.ModelForm):
    """ユーザー編集フォーム"""
    first_name = forms.CharField(
        label='名',
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    last_name = forms.CharField(
        label='姓',
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    email = forms.EmailField(
        label='メールアドレス',
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-input'})
    )
    is_active = forms.BooleanField(
        label='アクティブ',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )
    is_staff = forms.BooleanField(
        label='管理者権限',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )
    is_superuser = forms.BooleanField(
        label='スーパーユーザー権限',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff', 'is_superuser')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'ユーザー名'
        self.fields['username'].widget.attrs['readonly'] = True

class UserSearchForm(forms.Form):
    """ユーザー検索フォーム"""
    username = forms.CharField(
        label='ユーザー名',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'ユーザー名で検索'})
    )
    first_name = forms.CharField(
        label='氏名',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '氏名で検索'})
    )
    role = forms.ChoiceField(
        label='権限',
        required=False,
        choices=[
            ('', 'すべて'),
            ('admin', '管理者'),
            ('staff', '一般'),
            ('guest', 'ゲスト'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    ) 