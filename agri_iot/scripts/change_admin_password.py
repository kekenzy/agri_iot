#!/usr/bin/env python3
"""
adminユーザーのパスワードを変更するスクリプト
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

try:
    django.setup()
    from django.contrib.auth.models import User
    from django.contrib.auth.hashers import make_password
    
    def change_admin_password():
        """adminユーザーのパスワードを変更する"""
        try:
            # adminユーザーを検索
            try:
                admin_user = User.objects.get(username='admin')
                print(f"✅ adminユーザーが見つかりました: {admin_user.username}")
            except User.DoesNotExist:
                print("❌ adminユーザーが見つかりません")
                print("💡 先にadminユーザーを作成してください")
                return False
            
            # パスワードを変更
            new_password = 'Kekenji1'
            admin_user.password = make_password(new_password)
            admin_user.save()
            
            print(f"✅ adminユーザーのパスワードが変更されました")
            print(f"👤 ユーザー名: {admin_user.username}")
            print(f"📧 メールアドレス: {admin_user.email}")
            print(f"🔑 新しいパスワード: {new_password}")
            print("🎉 AWSのDjangoのadmin画面にログインできるようになりました！")
            return True
            
        except Exception as e:
            print(f"❌ パスワードの変更に失敗しました: {e}")
            import traceback
            traceback.print_exc()
            return False

    if __name__ == '__main__':
        success = change_admin_password()
        sys.exit(0 if success else 1)

except Exception as e:
    print(f"❌ Djangoの初期化に失敗しました: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 