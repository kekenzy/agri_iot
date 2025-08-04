#!/usr/bin/env python3
"""
AWS環境にスタイル設定の初期データを登録するスクリプト
"""

import os
import sys
import django

# Django設定を読み込み
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agri_iot.settings.production')
django.setup()

from agri_app.models import StyleSettings

def create_style_settings():
    """スタイル設定の初期データを作成"""
    
    print("🎨 スタイル設定の初期データを作成中...")
    
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
            print(f"  ✅ 作成: {config['name']} ({config['active_style']})")
            created_count += 1
        else:
            # 既存のデータがある場合は更新
            for key, value in config.items():
                setattr(style_setting, key, value)
            style_setting.save()
            print(f"  🔄 更新: {config['name']} ({config['active_style']})")
            updated_count += 1
    
    print(f"\n📊 結果:")
    print(f"  作成: {created_count}件")
    print(f"  更新: {updated_count}件")
    
    # 現在のスタイル設定を表示
    print(f"\n📋 現在のスタイル設定:")
    for setting in StyleSettings.objects.all():
        default_mark = " (デフォルト)" if setting.is_default else ""
        print(f"  - {setting.name}: {setting.active_style}{default_mark}")
    
    # アクティブなスタイルを確認
    active_style = StyleSettings.get_active_style()
    print(f"\n🎯 アクティブなスタイル: {active_style}")
    
    print("\n🎉 スタイル設定の初期化が完了しました！")

if __name__ == "__main__":
    try:
        create_style_settings()
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        sys.exit(1) 