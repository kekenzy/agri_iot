#!/usr/bin/env python3
"""
メール送信機能のテストスクリプト
"""
import os
import sys
import django

# Django設定を読み込み
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agri_iot.settings.local')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string

def test_email_sending():
    """メール送信機能をテスト"""
    print("=== メール送信テスト開始 ===")
    
    # 設定確認
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print(f"DEBUG: {settings.DEBUG}")
    
    # テスト用のメール送信
    try:
        subject = 'テストメール'
        message = 'これはテストメールです。'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = ['test@example.com']
        
        print(f"\nメール送信を試行中...")
        print(f"件名: {subject}")
        print(f"送信者: {from_email}")
        print(f"宛先: {recipient_list}")
        
        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=False,
        )
        
        print("✅ メール送信成功！")
        
    except Exception as e:
        print(f"❌ メール送信エラー: {e}")
        return False
    
    # パスワードリセットトークン生成テスト
    try:
        print(f"\n=== パスワードリセットトークン生成テスト ===")
        
        # ユーザーを取得（最初のユーザーを使用）
        users = User.objects.all()
        if users.exists():
            user = users.first()
            print(f"テストユーザー: {user.username} ({user.email})")
            
            # トークン生成
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            print(f"UID: {uid}")
            print(f"Token: {token}")
            
            # リセットURL生成
            reset_url = f"http://localhost:8000/agri_app/reset/{uid}/{token}"
            print(f"リセットURL: {reset_url}")
            
            # メールテンプレートテスト
            email_context = {
                'user': user,
                'reset_url': reset_url,
            }
            
            email_message = render_to_string('password_reset/password_reset_email.html', email_context)
            print(f"\n=== メールテンプレート内容 ===")
            print(email_message)
            
            print("✅ パスワードリセット機能テスト成功！")
            
        else:
            print("❌ ユーザーが見つかりません")
            return False
            
    except Exception as e:
        print(f"❌ パスワードリセットテストエラー: {e}")
        return False
    
    print("\n=== テスト完了 ===")
    return True

if __name__ == '__main__':
    test_email_sending() 