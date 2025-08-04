#!/bin/bash

# adminユーザー作成スクリプト
set -e

echo "🔐 adminユーザーを作成します..."

# 環境変数の設定
export DJANGO_SETTINGS_MODULE=agri_iot.settings.production

# データベース接続情報を取得
DATABASE_URL=$(aws secretsmanager get-secret-value --secret-id agri-iot/database-url --query SecretString --output text --region ap-northeast-1)
export DATABASE_URL

# SECRET_KEYを取得
SECRET_KEY=$(aws secretsmanager get-secret-value --secret-id agri-iot/secret-key --query SecretString --output text --region ap-northeast-1)
export SECRET_KEY

# AWS認証情報を取得
AWS_ACCESS_KEY_ID=$(aws secretsmanager get-secret-value --secret-id agri-iot/aws-access-key --query SecretString --output text --region ap-northeast-1)
export AWS_ACCESS_KEY_ID

AWS_SECRET_ACCESS_KEY=$(aws secretsmanager get-secret-value --secret-id agri-iot/aws-secret-key --query SecretString --output text --region ap-northeast-1)
export AWS_SECRET_ACCESS_KEY

# その他の環境変数
export AWS_STORAGE_BUCKET_NAME=agri-capture
export AWS_S3_REGION_NAME=ap-northeast-1

# adminユーザー作成スクリプトを実行
cd /tmp
python3 create_admin_script.py

echo "✅ adminユーザー作成が完了しました" 