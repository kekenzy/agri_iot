from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
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