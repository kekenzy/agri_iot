from django.core.management.base import BaseCommand
from agri_app.models import StyleSettings


class Command(BaseCommand):
    help = 'スタイル設定の初期データを作成します'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🎨 スタイル設定の初期データを作成中...'))
        
        # スタイル設定の初期データ
        style_configs = [
            {
                'name': 'デフォルト設定',
                'active_style': 'base',
                'is_default': True,
                'description': 'デフォルトのベーススタイル'
            },
            {
                'name': 'KUUMAスタイル',
                'active_style': 'kuuma',
                'is_default': False,
                'description': 'ミニマルで洗練されたKUUMAスタイル'
            },
            {
                'name': 'ダークテーマ',
                'active_style': 'dark',
                'is_default': False,
                'description': '目に優しいダークテーマ'
            },
            {
                'name': 'カラフルテーマ',
                'active_style': 'colorful',
                'is_default': False,
                'description': '明るくカラフルなテーマ'
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for config in style_configs:
            style_setting, created = StyleSettings.objects.get_or_create(
                name=config['name'],
                defaults=config
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'  ✅ 作成: {config["name"]} ({config["active_style"]})')
                )
                created_count += 1
            else:
                # 既存のデータがある場合は更新
                for key, value in config.items():
                    setattr(style_setting, key, value)
                style_setting.save()
                self.stdout.write(
                    self.style.WARNING(f'  🔄 更新: {config["name"]} ({config["active_style"]})')
                )
                updated_count += 1
        
        self.stdout.write(f'\n📊 結果:')
        self.stdout.write(f'  作成: {created_count}件')
        self.stdout.write(f'  更新: {updated_count}件')
        
        # 現在のスタイル設定を表示
        self.stdout.write(f'\n📋 現在のスタイル設定:')
        for setting in StyleSettings.objects.all():
            default_mark = " (デフォルト)" if setting.is_default else ""
            self.stdout.write(f'  - {setting.name}: {setting.active_style}{default_mark}')
        
        # アクティブなスタイルを確認
        active_style = StyleSettings.get_active_style()
        self.stdout.write(f'\n🎯 アクティブなスタイル: {active_style}')
        
        self.stdout.write(
            self.style.SUCCESS('\n🎉 スタイル設定の初期化が完了しました！')
        ) 