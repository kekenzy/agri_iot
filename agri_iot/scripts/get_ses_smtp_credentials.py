#!/usr/bin/env python3
"""
AWS SES SMTP認証情報を取得するスクリプト
"""

import boto3
import json
import os
from botocore.exceptions import ClientError

def get_ses_smtp_credentials():
    """
    AWS SES SMTP認証情報を取得する
    """
    try:
        # AWS SESクライアントを作成
        ses_client = boto3.client('ses', region_name='ap-northeast-1')
        
        # SMTP認証情報を取得
        response = ses_client.get_send_quota()
        
        # SMTP認証情報を取得（環境変数から）
        smtp_username = os.getenv('AWS_SES_SMTP_USERNAME')
        smtp_password = os.getenv('AWS_SES_SMTP_PASSWORD')
        
        if not smtp_username or not smtp_password:
            print("AWS_SES_SMTP_USERNAME または AWS_SES_SMTP_PASSWORD が設定されていません")
            return None
        
        credentials = {
            'smtp_username': smtp_username,
            'smtp_password': smtp_password,
            'smtp_host': 'email-smtp.ap-northeast-1.amazonaws.com',
            'smtp_port': 587,
            'send_quota': response
        }
        
        print("SES SMTP認証情報:")
        print(f"SMTP Host: {credentials['smtp_host']}")
        print(f"SMTP Port: {credentials['smtp_port']}")
        print(f"SMTP Username: {credentials['smtp_username']}")
        print(f"SMTP Password: {credentials['smtp_password']}")
        print(f"Send Quota: {credentials['send_quota']}")
        
        return credentials
        
    except ClientError as e:
        print(f"エラーが発生しました: {e}")
        return None
    except Exception as e:
        print(f"予期しないエラーが発生しました: {e}")
        return None

def test_ses_connection():
    """
    SES接続をテストする
    """
    try:
        # AWS SESクライアントを作成
        ses_client = boto3.client('ses', region_name='ap-northeast-1')
        
        # 送信統計を取得
        response = ses_client.get_send_statistics()
        
        print("SES接続テスト成功")
        print(f"送信統計: {len(response['SendDataPoints'])} 件のデータポイント")
        
        return True
        
    except ClientError as e:
        print(f"SES接続テスト失敗: {e}")
        return False
    except Exception as e:
        print(f"予期しないエラーが発生しました: {e}")
        return False

if __name__ == "__main__":
    print("AWS SES SMTP認証情報を取得中...")
    
    # SES接続をテスト
    if test_ses_connection():
        # SMTP認証情報を取得
        credentials = get_ses_smtp_credentials()
        
        if credentials:
            print("\n✅ SES SMTP認証情報の取得が完了しました")
        else:
            print("\n❌ SES SMTP認証情報の取得に失敗しました")
    else:
        print("\n❌ SES接続テストに失敗しました") 