from django import template
from django.template.defaulttags import register
from agri_app.models import StyleSettings

register = template.Library()

@register.simple_tag
def get_active_style():
    """現在アクティブなスタイルを取得するテンプレートタグ"""
    return StyleSettings.get_active_style() 