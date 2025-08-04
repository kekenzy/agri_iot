# Generated manually for Announcement email fields

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('agri_app', '0003_emailsettings'),
    ]

    operations = [
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_at', models.DateTimeField(default=django.utils.timezone.datetime.now)),
                ('update_at', models.DateTimeField(default=django.utils.timezone.datetime.now)),
                ('title', models.CharField(max_length=200, verbose_name='タイトル')),
                ('content', models.TextField(verbose_name='内容')),
                ('priority', models.CharField(choices=[('low', '低'), ('normal', '通常'), ('high', '高'), ('urgent', '緊急')], default='normal', max_length=10, verbose_name='優先度')),
                ('start_date', models.DateTimeField(verbose_name='表示開始日時')),
                ('end_date', models.DateTimeField(verbose_name='表示終了日時')),
                ('is_all_groups', models.BooleanField(default=False, verbose_name='全てのグループに通知')),
                ('is_active', models.BooleanField(default=True, verbose_name='アクティブ')),
                ('send_email', models.BooleanField(default=False, verbose_name='メール送信')),
                ('email_sent', models.BooleanField(default=False, verbose_name='メール送信済み')),
                ('email_sent_at', models.DateTimeField(blank=True, null=True, verbose_name='メール送信日時')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user', verbose_name='作成者')),
                ('target_groups', models.ManyToManyField(blank=True, to='auth.group', verbose_name='通知先グループ')),
            ],
            options={
                'verbose_name': 'お知らせ',
                'verbose_name_plural': 'お知らせ',
                'db_table': 'announcement',
                'db_table_comment': 'お知らせ',
                'ordering': ['-priority', '-start_date'],
            },
        ),
    ] 