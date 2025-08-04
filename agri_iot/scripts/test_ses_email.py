#!/usr/bin/env python3
"""
SESを使用したメール送信テストスクリプト
"""

import os
import sys
import django

# Django設定を読み込み
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agri_iot.settings.production')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_ses_email():
    """SESを使用してメール送信をテスト"""
    
    print("📧 SESメール送信テストを開始...")
    
    # テスト用のメール設定
    subject = "SESメール送信テスト"
    message = """
これはAWS SESを使用したメール送信テストです。

設定内容:
- EMAIL_BACKEND: {backend}
- AWS_SES_REGION_NAME: {region}
- DEFAULT_FROM_EMAIL: {from_email}

このメールが正常に送信されれば、SESの設定は成功です。
""".format(
        backend=settings.EMAIL_BACKEND,
        region=getattr(settings, 'AWS_SES_REGION_NAME', 'Not set'),
        from_email=settings.DEFAULT_FROM_EMAIL
    )
    
    # テスト用の送信先メールアドレス（実際のメールアドレスに変更してください）
    recipient_list = ['test@example.com']  # 実際のメールアドレスに変更
    
    try:
        print(f"📤 メール送信中...")
        print(f"  送信者: {settings.DEFAULT_FROM_EMAIL}")
        print(f"  送信先: {recipient_list}")
        print(f"  件名: {subject}")
        
        # メール送信
        result = send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            fail_silently=False
        )
        
        if result:
            print("✅ メール送信成功！")
            print(f"  送信されたメール数: {result}")
        else:
            print("❌ メール送信失敗")
            
    except Exception as e:
        print(f"❌ メール送信エラー: {e}")
        print(f"   エラータイプ: {type(e).__name__}")
        
        # 設定情報を表示
        print("\n📋 現在のメール設定:")
        print(f"  EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        print(f"  AWS_SES_REGION_NAME: {getattr(settings, 'AWS_SES_REGION_NAME', 'Not set')}")
        print(f"  DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
        print(f"  AWS_ACCESS_KEY_ID: {os.environ.get('AWS_ACCESS_KEY_ID', 'Not set')}")
        print(f"  AWS_SECRET_ACCESS_KEY: {'Set' if os.environ.get('AWS_SECRET_ACCESS_KEY') else 'Not set'}")

if __name__ == "__main__":
    try:
        test_ses_email()
    except Exception as e:
        print(f"❌ スクリプト実行エラー: {e}")
        sys.exit(1) 