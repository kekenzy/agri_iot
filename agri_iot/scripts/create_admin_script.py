#!/usr/bin/env python3
"""
adminユーザーを作成するためのスタンドアロンスクリプト
"""
import os
import sys
import django
from pathlib import Path

# Django設定を読み込み
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agri_iot.settings.production')
django.setup()

from django.contrib.auth.models import User

def create_admin_user():
    """adminユーザーを作成する"""
    try:
        # 既存のadminユーザーをチェック
        if User.objects.filter(username='admin').exists():
            print("✅ adminユーザーは既に存在します")
            return True
        
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
        return True
        
    except Exception as e:
        print(f"❌ adminユーザーの作成に失敗しました: {e}")
        return False

if __name__ == '__main__':
    success = create_admin_user()
    sys.exit(0 if success else 1) 