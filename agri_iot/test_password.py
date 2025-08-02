#!/usr/bin/env python
"""
パスワード認証をテストするスクリプト
"""

import os
import sys
import django

# Djangoの設定を読み込み
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agri_iot.settings.local')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

def test_password(username, password):
    """パスワード認証をテスト"""
    print(f"=== パスワード認証テスト ===")
    print(f"ユーザー名: {username}")
    print(f"パスワード: {password}")
    
    # ユーザーの存在確認
    try:
        user = User.objects.get(username=username)
        print(f"ユーザー発見: {user.username}")
        print(f"メールアドレス: {user.email}")
        print(f"アクティブ: {user.is_active}")
        print(f"パスワードハッシュ: {user.password[:50]}...")
    except User.DoesNotExist:
        print(f"ユーザー '{username}' が見つかりません。")
        return
    
    # 認証テスト
    authenticated_user = authenticate(username=username, password=password)
    if authenticated_user:
        print("✅ 認証成功")
        print(f"認証されたユーザー: {authenticated_user.username}")
    else:
        print("❌ 認証失敗")
        print("パスワードが間違っているか、ユーザーが非アクティブです。")

def test_email_login(email, password):
    """メールアドレスでのログインをテスト"""
    print(f"=== メールアドレスログインテスト ===")
    print(f"メールアドレス: {email}")
    print(f"パスワード: {password}")
    
    # メールアドレスでユーザーを検索
    try:
        user = User.objects.get(email__iexact=email)
        print(f"メールアドレスでユーザー発見: {user.username}")
        
        # ユーザー名で認証
        authenticated_user = authenticate(username=user.username, password=password)
        if authenticated_user:
            print("✅ メールアドレス経由での認証成功")
            print(f"認証されたユーザー: {authenticated_user.username}")
        else:
            print("❌ メールアドレス経由での認証失敗")
    except User.DoesNotExist:
        print(f"メールアドレス '{email}' でユーザーが見つかりません。")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("使用方法:")
        print("python test_password.py <username> <password>")
        print("python test_password.py --email <email> <password>")
        sys.exit(1)
    
    if sys.argv[1] == "--email":
        if len(sys.argv) < 4:
            print("メールアドレスの場合はパスワードも指定してください。")
            sys.exit(1)
        test_email_login(sys.argv[2], sys.argv[3])
    else:
        test_password(sys.argv[1], sys.argv[2]) 