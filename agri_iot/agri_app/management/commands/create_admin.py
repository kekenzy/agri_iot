from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'adminユーザーを作成します'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            default='admin',
            help='作成するユーザー名（デフォルト: admin）'
        )
        parser.add_argument(
            '--email',
            default='admin@agri-iot.com',
            help='メールアドレス（デフォルト: admin@agri-iot.com）'
        )
        parser.add_argument(
            '--password',
            default='admin123456',
            help='パスワード（デフォルト: admin123456）'
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        try:
            # 既存のユーザーをチェック
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {username}ユーザーは既に存在します')
                )
                return

            # スーパーユーザーを作成
            admin_user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )

            self.stdout.write(
                self.style.SUCCESS(f'✅ {username}ユーザーが作成されました')
            )
            self.stdout.write(f'📧 メールアドレス: {email}')
            self.stdout.write(f'🔑 パスワード: {password}')
            self.stdout.write(
                self.style.WARNING('⚠️  本番環境では必ずパスワードを変更してください')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ ユーザーの作成に失敗しました: {e}')
            )
            raise 