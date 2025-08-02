from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User, Group
from django.contrib.auth.models import Permission
# from django.contrib.auth.models import (
#   BaseUserManager, AbstractBaseUser, PermissionsMixin
# )

class BaseMeta(models.Model):
  create_at = models.DateTimeField(default=timezone.datetime.now)
  update_at = models.DateTimeField(default=timezone.datetime.now)

  class Meta:
    abstract = True

class UserProfile(BaseMeta):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  picture = models.FileField(upload_to='user/', blank=True)

  # name = models.CharField(max_length=50, db_comment='名前')
  # email = models.EmailField(db_index=True, null=True, db_comment='メールアドレス')

  class Meta:
    db_table = 'user_profile'
    db_table_comment = 'ユーザ'
    # index_together

  def __str__(self):
      # return self.name
      return self.user.username

class GroupProfile(BaseMeta):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True, verbose_name='説明')
    is_active = models.BooleanField(default=True, verbose_name='アクティブ')
    color = models.CharField(max_length=7, default='#667eea', verbose_name='グループカラー')
    
    class Meta:
        db_table = 'group_profile'
        db_table_comment = 'グループプロフィール'
        verbose_name = 'グループプロフィール'
        verbose_name_plural = 'グループプロフィール'
    
    def __str__(self):
        return self.group.name
    
    def get_member_count(self):
        return self.group.user_set.count()
    
    def get_permissions_display(self):
        return ', '.join([perm.name for perm in self.group.permissions.all()[:5]])