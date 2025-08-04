#!/usr/bin/env python
"""
Django管理コマンドでadminユーザーを作成するスクリプト
"""
import os
import sys
import django

# Django設定を読み込み
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agri_iot.settings.production')
django.setup()

from django.contrib.auth.models import User
from django.core.management import execute_from_command_line

def create_admin_user():
    """adminユーザーを作成する"""
    try:
        # 既存のadminユーザーをチェック
        if User.objects.filter(username='admin').exists():
            print("✅ adminユーザーは既に存在します")
            return
        
        # adminユーザーを作成
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@agri-iot.com',
            password='admin123456'
        )
        
        print(f"✅ adminユーザーが作成されました: {admin_user.username}")
        print("📧 メールアドレス: admin@agri-iot.com")
        print("🔑 パスワード: admin123456")
        print("⚠️  本番環境では必ずパスワードを変更してください")
        
    except Exception as e:
        print(f"❌ adminユーザーの作成に失敗しました: {e}")
        sys.exit(1)

if __name__ == '__main__':
    create_admin_user() 