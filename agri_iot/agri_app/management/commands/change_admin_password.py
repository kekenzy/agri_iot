from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

class Command(BaseCommand):
    help = 'adminユーザーのパスワードを変更します'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            default='admin',
            help='パスワードを変更するユーザー名（デフォルト: admin）'
        )
        parser.add_argument(
            '--password',
            default='Kekenji1',
            help='新しいパスワード（デフォルト: Kekenji1）'
        )

    def handle(self, *args, **options):
        username = options['username']
        new_password = options['password']

        try:
            # ユーザーを検索
            try:
                user = User.objects.get(username=username)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {username}ユーザーが見つかりました')
                )
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ {username}ユーザーが見つかりません')
                )
                self.stdout.write('💡 先にadminユーザーを作成してください')
                return

            # パスワードを変更
            user.password = make_password(new_password)
            user.save()

            self.stdout.write(
                self.style.SUCCESS(f'✅ {username}ユーザーのパスワードが変更されました')
            )
            self.stdout.write(f'👤 ユーザー名: {username}')
            self.stdout.write(f'📧 メールアドレス: {user.email}')
            self.stdout.write(f'🔑 新しいパスワード: {new_password}')
            self.stdout.write(
                self.style.SUCCESS('🎉 AWSのDjangoのadmin画面にログインできるようになりました！')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ パスワードの変更に失敗しました: {e}')
            )
            raise 