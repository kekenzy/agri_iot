#!/usr/bin/env python
"""
データベース内のユーザー情報を確認するスクリプト
"""

import os
import sys
import django

# Djangoの設定を読み込み
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agri_iot.settings.local')
django.setup()

from django.contrib.auth.models import User

def check_users():
    """データベース内のユーザー情報を表示"""
    print("=== データベース内のユーザー情報 ===")
    users = User.objects.all()
    
    if not users.exists():
        print("ユーザーが存在しません。")
        return
    
    for user in users:
        print(f"ID: {user.id}")
        print(f"ユーザー名: {user.username}")
        print(f"メールアドレス: {user.email}")
        print(f"姓: {user.last_name}")
        print(f"名: {user.first_name}")
        print(f"アクティブ: {user.is_active}")
        print(f"スタッフ: {user.is_staff}")
        print(f"スーパーユーザー: {user.is_superuser}")
        print(f"作成日: {user.date_joined}")
        print(f"最終ログイン: {user.last_login}")
        print("-" * 50)

def check_specific_user(username_or_email):
    """特定のユーザー情報を確認"""
    print(f"=== ユーザー '{username_or_email}' の情報 ===")
    
    # ユーザー名で検索
    try:
        user = User.objects.get(username=username_or_email)
        print(f"ユーザー名で発見: {user.username}")
        print_user_info(user)
        return
    except User.DoesNotExist:
        print(f"ユーザー名 '{username_or_email}' では見つかりませんでした。")
    
    # メールアドレスで検索
    try:
        user = User.objects.get(email__iexact=username_or_email)
        print(f"メールアドレスで発見: {user.email}")
        print_user_info(user)
        return
    except User.DoesNotExist:
        print(f"メールアドレス '{username_or_email}' でも見つかりませんでした。")
    
    print("ユーザーが見つかりませんでした。")

def print_user_info(user):
    """ユーザー情報を表示"""
    print(f"ID: {user.id}")
    print(f"ユーザー名: {user.username}")
    print(f"メールアドレス: {user.email}")
    print(f"姓: {user.last_name}")
    print(f"名: {user.first_name}")
    print(f"アクティブ: {user.is_active}")
    print(f"スタッフ: {user.is_staff}")
    print(f"スーパーユーザー: {user.is_superuser}")
    print(f"作成日: {user.date_joined}")
    print(f"最終ログイン: {user.last_login}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 特定のユーザーを確認
        check_specific_user(sys.argv[1])
    else:
        # 全ユーザーを確認
        check_users() 