from django.core.exceptions import ValidationError
import re

class CustomPasswordValidator():
  def __init__(self):
    pass
  
  def validate(self, password, user=None):
    if all((re.search('[0-9]', password), re.search('[a-z]', password), re.search('[A-Z]', password))):
      return
    raise ValidationError('パスワードには、0-9, a-z, A-Zを含んでください')

  def get_help_text(self):
    # 管理画面などで表示されるヒントを書く
    return '※パスワード忘れた場合は問い合わせもらえれば再度設定できるので気にしないでね'

    