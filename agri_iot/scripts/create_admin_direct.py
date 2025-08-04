#!/usr/bin/env python3
"""
RDSに直接接続してadminユーザーを作成するスクリプト
"""
import os
import sys
import django
from pathlib import Path

# Django設定を読み込み
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# 環境変数を設定
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agri_iot.settings.production')

# データベース接続情報を直接設定
os.environ['DATABASE_URL'] = 'postgresql://agri_user:agri_password@agri-iot-db.ceswvgqkwv57.ap-northeast-1.rds.amazonaws.com:5432/agri_db'
os.environ['SECRET_KEY'] = 'j=d@d-i=^d4$e%1p50lk529i5nr80dv)3)wycowclea2t)1vy3'
os.environ['AWS_ACCESS_KEY_ID'] = 'AKIAWNHBWGAAVHMPGRL5'
os.environ['AWS_SECRET_ACCESS_KEY'] = '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'
os.environ['AWS_STORAGE_BUCKET_NAME'] = 'agri-capture'
os.environ['AWS_S3_REGION_NAME'] = 'ap-northeast-1'

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
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = create_admin_user()
    sys.exit(0 if success else 1) 