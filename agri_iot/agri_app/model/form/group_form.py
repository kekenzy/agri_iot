from django import forms
from django.contrib.auth.models import Group
from agri_app.models import GroupProfile

class GroupSearchForm(forms.Form):
    name = forms.CharField(
        label='グループ名',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'グループ名で検索'
        })
    )
    is_active = forms.ChoiceField(
        label='ステータス',
        required=False,
        choices=[
            ('', 'すべて'),
            ('True', 'アクティブ'),
            ('False', '非アクティブ')
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'グループ名を入力'
            })
        }

class GroupProfileForm(forms.ModelForm):
    class Meta:
        model = GroupProfile
        fields = ['description', 'is_active', 'color']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'グループの説明を入力'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-input',
                'type': 'color'
            })
        }

class GroupMemberForm(forms.Form):
    users = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='メンバー'
    )
    
    def __init__(self, *args, **kwargs):
        group = kwargs.pop('group', None)
        super().__init__(*args, **kwargs)
        if group:
            from django.contrib.auth.models import User
            self.fields['users'].queryset = User.objects.all()
            self.fields['users'].initial = group.user_set.all() 