from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User, Group
from django.contrib.auth.models import Permission
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
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
    send_email = models.BooleanField(default=False, verbose_name='メール送信')
    email_sent = models.BooleanField(default=False, verbose_name='メール送信済み')
    email_sent_at = models.DateTimeField(null=True, blank=True, verbose_name='メール送信日時')
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
            return user.groups.filter(id__in=self.target_groups.values_list('id', flat=True)).exists()
        
        return False
    
    def get_priority_display(self):
        """優先度の表示名を取得"""
        return dict(self.PRIORITY_CHOICES).get(self.priority, self.priority)
    
    def get_priority_class(self):
        """優先度に応じたCSSクラスを取得"""
        priority_classes = {
            'urgent': 'badge-urgent',
            'high': 'badge-high',
            'normal': 'badge-normal',
            'low': 'badge-low',
        }
        return priority_classes.get(self.priority, 'badge-normal')
    
    def get_priority_icon(self):
        """優先度に応じたアイコンを取得"""
        priority_icons = {
            'urgent': '🚨',
            'high': '⚠️',
            'normal': '📢',
            'low': 'ℹ️',
        }
        return priority_icons.get(self.priority, '📢')
    
    def get_target_groups_display(self):
        """対象グループの表示名を取得"""
        if self.is_all_groups:
            return "全てのグループ"
        elif self.target_groups.exists():
            return ", ".join([group.name for group in self.target_groups.all()])
        else:
            return "指定なし"
    
    def get_target_users(self):
        """メール送信対象のユーザーを取得"""
        if self.is_all_groups:
            # 全てのアクティブユーザー
            return User.objects.filter(is_active=True)
        elif self.target_groups.exists():
            # 指定されたグループのメンバー
            return User.objects.filter(
                is_active=True,
                groups__in=self.target_groups.all()
            ).distinct()
        else:
            return User.objects.none()
    
    def send_announcement_email(self):
        """お知らせメールを送信"""
        if not self.send_email or self.email_sent:
            return False
        
        target_users = self.get_target_users()
        if not target_users.exists():
            return False
        
        # メールテンプレートの準備
        context = {
            'announcement': self,
            'priority_display': self.get_priority_display(),
            'priority_icon': self.get_priority_icon(),
            'target_groups_display': self.get_target_groups_display(),
        }
        
        # HTMLメールの作成
        html_message = render_to_string('emails/announcement_notification.html', context)
        plain_message = strip_tags(html_message)
        
        # 件名の作成
        subject = f"[{self.get_priority_display()}] {self.title}"
        
        # 送信者
        from_email = settings.DEFAULT_FROM_EMAIL
        
        # 各ユーザーにメール送信
        success_count = 0
        failed_users = []
        for user in target_users:
            if user.email:
                try:
                    send_mail(
                        subject=subject,
                        message=plain_message,
                        from_email=from_email,
                        recipient_list=[user.email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                    success_count += 1
                except Exception as e:
                    failed_users.append({
                        'user': user.username,
                        'email': user.email,
                        'error': str(e)
                    })
                    print(f"メール送信エラー (ユーザー: {user.username}): {e}")
        
        # 送信完了フラグを更新
        if success_count > 0:
            self.email_sent = True
            self.email_sent_at = timezone.now()
            self.save(update_fields=['email_sent', 'email_sent_at'])
        
        return {
            'success_count': success_count,
            'total_count': target_users.count(),
            'failed_users': failed_users
        }
    
    def send_manual_email(self):
        """手動でメール送信を実行（既に送信済みでも再送信可能）"""
        target_users = self.get_target_users()
        if not target_users.exists():
            return {
                'success_count': 0,
                'total_count': 0,
                'failed_users': [],
                'error': '送信対象ユーザーが見つかりません'
            }
        
        # メールテンプレートの準備
        context = {
            'announcement': self,
            'priority_display': self.get_priority_display(),
            'priority_icon': self.get_priority_icon(),
            'target_groups_display': self.get_target_groups_display(),
        }
        
        # HTMLメールの作成
        html_message = render_to_string('emails/announcement_notification.html', context)
        plain_message = strip_tags(html_message)
        
        # 件名の作成
        subject = f"[{self.get_priority_display()}] {self.title}"
        
        # 送信者
        from_email = settings.DEFAULT_FROM_EMAIL
        
        # 各ユーザーにメール送信
        success_count = 0
        failed_users = []
        for user in target_users:
            if user.email:
                try:
                    send_mail(
                        subject=subject,
                        message=plain_message,
                        from_email=from_email,
                        recipient_list=[user.email],
                        html_message=html_message,
                        fail_silently=False,
                    )
                    success_count += 1
                except Exception as e:
                    failed_users.append({
                        'user': user.username,
                        'email': user.email,
                        'error': str(e)
                    })
                    print(f"メール送信エラー (ユーザー: {user.username}): {e}")
        
        # 送信完了フラグを更新
        if success_count > 0:
            self.email_sent = True
            self.email_sent_at = timezone.now()
            self.save(update_fields=['email_sent', 'email_sent_at'])
        
        return {
            'success_count': success_count,
            'total_count': target_users.count(),
            'failed_users': failed_users
        }
    
    def get_email_status_display(self):
        """メール送信状況の表示用テキストを取得"""
        if not self.send_email:
            return "無効"
        elif self.email_sent:
            return f"送信済み ({self.email_sent_at.strftime('%Y/%m/%d %H:%M')})"
        else:
            return "送信予定"
    
    def get_email_status_class(self):
        """メール送信状況に応じたCSSクラスを取得"""
        if not self.send_email:
            return "badge-inactive"
        elif self.email_sent:
            return "badge-success"
        else:
            return "badge-warning"
    
    def can_send_email(self):
        """メール送信可能かどうかを判定"""
        return (
            self.send_email and 
            self.is_active and 
            self.is_currently_active() and
            self.get_target_users().exists()
        )
    
    def save(self, *args, **kwargs):
        """保存時にメール送信を実行"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # 新規作成時でメール送信が有効な場合
        if is_new and self.send_email:
            self.send_announcement_email()

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


class EmailSettings(BaseMeta):
    """メール送信設定を管理するモデル"""
    name = models.CharField(max_length=50, verbose_name='設定名', unique=True)
    default_send_email = models.BooleanField(default=False, verbose_name='デフォルトでメール送信を有効にする')
    email_template_subject = models.CharField(
        max_length=200, 
        default='[{priority}] {title}',
        verbose_name='メール件名テンプレート'
    )
    email_from_name = models.CharField(
        max_length=100, 
        default='お知らせシステム',
        verbose_name='送信者名'
    )
    is_default = models.BooleanField(default=False, verbose_name='デフォルト設定')
    description = models.TextField(blank=True, null=True, verbose_name='説明')
    
    class Meta:
        db_table = 'email_settings'
        db_table_comment = 'メール送信設定'
        verbose_name = 'メール送信設定'
        verbose_name_plural = 'メール送信設定'
    
    def __str__(self):
        return f"{self.name} (デフォルト送信: {'有効' if self.default_send_email else '無効'})"
    
    def save(self, *args, **kwargs):
        # デフォルト設定の場合、他の設定のデフォルトフラグをFalseにする
        if self.is_default:
            EmailSettings.objects.exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
    
    @classmethod
    def get_default_settings(cls):
        """デフォルトのメール設定を取得"""
        try:
            default_setting = cls.objects.filter(is_default=True).first()
            if default_setting:
                return default_setting
        except:
            pass
        return None
    
    @classmethod
    def get_default_send_email(cls):
        """デフォルトのメール送信設定を取得"""
        default_settings = cls.get_default_settings()
        if default_settings:
            return default_settings.default_send_email
        return False