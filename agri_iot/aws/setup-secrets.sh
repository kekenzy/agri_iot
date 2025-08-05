#!/bin/bash

# AWS Secrets Manager設定スクリプト
echo "🔐 AWS Secrets Managerに機密情報を保存します..."

# 設定
AWS_REGION="ap-northeast-1"
PROJECT_NAME="agri-iot"

# 1. データベース接続情報
echo "📊 データベース接続情報を保存中..."
aws secretsmanager create-secret \
    --name "$PROJECT_NAME/database-url" \
    --description "Database connection URL for Agri IoT application" \
    --secret-string "{\"url\":\"postgresql://agri_user:${DB_PASSWORD}@agri-iot-db.xxxxx.ap-northeast-1.rds.amazonaws.com:5432/agri_db\"}" \
    --region $AWS_REGION

# 2. Django SECRET_KEY
echo "🔑 Django SECRET_KEYを生成・保存中..."
SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
aws secretsmanager create-secret \
    --name "$PROJECT_NAME/secret-key" \
    --description "Django SECRET_KEY for Agri IoT application" \
    --secret-string "$SECRET_KEY" \
    --region $AWS_REGION

# 3. AWS認証情報
echo "🔑 AWS認証情報を保存中..."
aws secretsmanager create-secret \
    --name "$PROJECT_NAME/aws-access-key" \
    --description "AWS Access Key ID for Agri IoT application" \
    --secret-string "${AWS_ACCESS_KEY_ID}" \
    --region $AWS_REGION

aws secretsmanager create-secret \
    --name "$PROJECT_NAME/aws-secret-key" \
    --description "AWS Secret Access Key for Agri IoT application" \
    --secret-string "${AWS_SECRET_ACCESS_KEY}" \
    --region $AWS_REGION

# 4. メール設定（必要に応じて更新）
echo "📧 メール設定を保存中..."
aws secretsmanager create-secret \
    --name "$PROJECT_NAME/email-host-user" \
    --description "Email host user for Agri IoT application" \
    --secret-string "${EMAIL_HOST_USER}" \
    --region $AWS_REGION

aws secretsmanager create-secret \
    --name "$PROJECT_NAME/email-host-password" \
    --description "Email host password for Agri IoT application" \
    --secret-string "${EMAIL_HOST_PASSWORD}" \
    --region $AWS_REGION

echo "✅ すべての機密情報がSecrets Managerに保存されました！"
echo ""
echo "📋 保存されたシークレット:"
echo "- $PROJECT_NAME/database-url"
echo "- $PROJECT_NAME/secret-key"
echo "- $PROJECT_NAME/aws-access-key"
echo "- $PROJECT_NAME/aws-secret-key"
echo "- $PROJECT_NAME/email-host-user"
echo "- $PROJECT_NAME/email-host-password" 