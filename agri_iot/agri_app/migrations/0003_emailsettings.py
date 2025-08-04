# Generated manually for EmailSettings model

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('agri_app', '0002_groupprofile'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_at', models.DateTimeField(default=django.utils.timezone.datetime.now)),
                ('update_at', models.DateTimeField(default=django.utils.timezone.datetime.now)),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='設定名')),
                ('default_send_email', models.BooleanField(default=False, verbose_name='デフォルトでメール送信を有効にする')),
                ('email_template_subject', models.CharField(default='[{priority}] {title}', max_length=200, verbose_name='メール件名テンプレート')),
                ('email_from_name', models.CharField(default='お知らせシステム', max_length=100, verbose_name='送信者名')),
                ('is_default', models.BooleanField(default=False, verbose_name='デフォルト設定')),
                ('description', models.TextField(blank=True, null=True, verbose_name='説明')),
            ],
            options={
                'verbose_name': 'メール送信設定',
                'verbose_name_plural': 'メール送信設定',
                'db_table': 'email_settings',
                'db_table_comment': 'メール送信設定',
            },
        ),
    ] 