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

class Announcement(BaseMeta):
    """お知らせを管理するモデル"""
    PRIORITY_CHOICES = [
        ('low', '低'),
        ('normal', '通常'),
        ('high', '高'),
        ('urgent', '緊急'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='タイトル')
    content = models.TextField(verbose_name='内容')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal', verbose_name='優先度')
    start_date = models.DateTimeField(verbose_name='表示開始日時')
    end_date = models.DateTimeField(verbose_name='表示終了日時')
    target_groups = models.ManyToManyField(Group, blank=True, verbose_name='通知先グループ')
    is_all_groups = models.BooleanField(default=False, verbose_name='全てのグループに通知')
    is_active = models.BooleanField(default=True, verbose_name='アクティブ')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='作成者')
    
    class Meta:
        db_table = 'announcement'
        db_table_comment = 'お知らせ'
        verbose_name = 'お知らせ'
        verbose_name_plural = 'お知らせ'
        ordering = ['-priority', '-start_date']
    
    def __str__(self):
        return self.title
    
    def is_currently_active(self):
        """現在表示すべきお知らせかどうかを判定"""
        now = timezone.now()
        return (
            self.is_active and 
            self.start_date <= now <= self.end_date
        )
    
    def is_visible_to_user(self, user):
        """指定されたユーザーに表示すべきお知らせかどうかを判定"""
        if not self.is_currently_active():
            return False
        
        # 全てのグループに通知する場合
        if self.is_all_groups:
            return True
        
        # 特定のグループに通知する場合
        if self.target_groups.exists():
            user_groups = user.groups.all()
            return self.target_groups.filter(id__in=user_groups.values_list('id', flat=True)).exists()
        
        # グループが指定されていない場合は表示しない
        return False
    
    def get_priority_class(self):
        """優先度に応じたCSSクラスを取得"""
        priority_classes = {
            'low': 'priority-low',
            'normal': 'priority-normal',
            'high': 'priority-high',
            'urgent': 'priority-urgent',
        }
        return priority_classes.get(self.priority, 'priority-normal')
    
    def get_priority_icon(self):
        """優先度に応じたアイコンを取得"""
        priority_icons = {
            'low': '📢',
            'normal': '📢',
            'high': '⚠️',
            'urgent': '🚨',
        }
        return priority_icons.get(self.priority, '📢')
    
    def get_target_groups_display(self):
        """対象グループの表示用文字列を取得"""
        if self.is_all_groups:
            return "全てのグループ"
        elif self.target_groups.exists():
            return ", ".join([group.name for group in self.target_groups.all()])
        else:
            return "指定なし"

class StyleSettings(BaseMeta):
    """スタイル設定を管理するモデル"""
    STYLE_CHOICES = [
        ('base', 'ベーススタイル'),
        ('kuuma', 'KUUMAスタイル'),
        ('dark', 'ダークテーマ'),
        ('colorful', 'カラフルテーマ'),
    ]
    
    name = models.CharField(max_length=50, verbose_name='設定名', unique=True)
    active_style = models.CharField(
        max_length=20, 
        choices=STYLE_CHOICES, 
        default='base', 
        verbose_name='アクティブスタイル'
    )
    is_default = models.BooleanField(default=False, verbose_name='デフォルト設定')
    description = models.TextField(blank=True, null=True, verbose_name='説明')
    
    class Meta:
        db_table = 'style_settings'
        db_table_comment = 'スタイル設定'
        verbose_name = 'スタイル設定'
        verbose_name_plural = 'スタイル設定'
    
    def __str__(self):
        return f"{self.name} ({self.get_active_style_display()})"
    
    def save(self, *args, **kwargs):
        # デフォルト設定の場合、他の設定のデフォルトフラグをFalseにする
        if self.is_default:
            StyleSettings.objects.exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
    
    @classmethod
    def get_active_style(cls):
        """現在アクティブなスタイルを取得"""
        try:
            default_setting = cls.objects.filter(is_default=True).first()
            if default_setting:
                return default_setting.active_style
        except:
            pass
        return 'base'  # デフォルトはベーススタイル