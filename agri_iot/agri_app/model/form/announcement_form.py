from django import forms
from django.contrib.auth.models import Group
from agri_app.models import Announcement


class AnnouncementForm(forms.ModelForm):
    """お知らせ作成・編集用フォーム"""
    
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'priority', 'start_date', 'end_date', 'target_groups', 'is_all_groups', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'お知らせのタイトルを入力してください'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'お知らせの内容を入力してください'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-control'
            }),
            'start_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'target_groups': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': 5
            }),
            'is_all_groups': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # グループの選択肢を設定
        self.fields['target_groups'].queryset = Group.objects.all()
        self.fields['target_groups'].required = False
        self.fields['is_all_groups'].required = False
        
        # 全てのグループが選択されている場合、グループ選択を無効化
        if self.instance.pk and self.instance.is_all_groups:
            self.fields['target_groups'].widget.attrs['disabled'] = 'disabled'
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        is_all_groups = cleaned_data.get('is_all_groups')
        target_groups = cleaned_data.get('target_groups')
        
        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError('表示開始日時は表示終了日時より前である必要があります。')
        
        # 全てのグループが選択されている場合、特定のグループ選択は無効
        if is_all_groups and target_groups:
            raise forms.ValidationError('「全てのグループに通知」が選択されている場合、特定のグループは選択できません。')
        
        # 全てのグループが選択されていない場合、少なくとも1つのグループを選択する必要がある
        if not is_all_groups and not target_groups:
            raise forms.ValidationError('「全てのグループに通知」を選択するか、少なくとも1つのグループを選択してください。')
        
        return cleaned_data


class AnnouncementSearchForm(forms.Form):
    """お知らせ検索用フォーム"""
    
    STATUS_CHOICES = [
        ('', 'すべて'),
        ('active', '表示中'),
        ('inactive', '非表示'),
        ('expired', '期限切れ'),
        ('future', '予定'),
    ]
    
    TARGET_TYPE_CHOICES = [
        ('', 'すべて'),
        ('all_groups', '全てのグループ'),
        ('specific_groups', '特定のグループ'),
    ]
    
    keyword = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'タイトルまたは内容で検索'
        }),
        label='キーワード'
    )
    
    priority = forms.ChoiceField(
        choices=[('', 'すべて')] + Announcement.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='優先度'
    )
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='ステータス'
    )
    
    target_type = forms.ChoiceField(
        choices=TARGET_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='対象タイプ'
    )
    
    target_group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='対象グループ'
    ) 