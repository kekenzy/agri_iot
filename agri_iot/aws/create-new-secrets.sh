#!/bin/bash

# AWS Secrets Manager新規作成スクリプト
set -e

# 設定
AWS_REGION="ap-northeast-1"
PROJECT_NAME="agri-iot"

echo "🔐 AWS Secrets Managerに新しい機密情報を作成します..."

# 環境変数の確認
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ] || [ -z "$DB_PASSWORD" ]; then
    echo "❌ 必要な環境変数が設定されていません"
    echo "AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, DB_PASSWORD を設定してください"
    exit 1
fi

# 1. データベース接続情報を作成
echo "📊 データベース接続情報を作成中..."
aws secretsmanager create-secret \
    --name "$PROJECT_NAME/database-url-new" \
    --description "Database connection URL for Agri IoT application" \
    --secret-string "{\"url\":\"postgresql://agri_user:${DB_PASSWORD}@agri-iot-db.ceswvgqkwv57.ap-northeast-1.rds.amazonaws.com:5432/agri_db\"}" \
    --region $AWS_REGION

# 2. Django SECRET_KEYを作成
echo "🔑 Django SECRET_KEYを作成中..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
aws secretsmanager create-secret \
    --name "$PROJECT_NAME/secret-key-new" \
    --description "Django SECRET_KEY for Agri IoT application" \
    --secret-string "$SECRET_KEY" \
    --region $AWS_REGION

# 3. AWS認証情報を作成
echo "🔑 AWS認証情報を作成中..."
aws secretsmanager create-secret \
    --name "$PROJECT_NAME/aws-access-key-new" \
    --description "AWS Access Key ID for Agri IoT application" \
    --secret-string "$AWS_ACCESS_KEY_ID" \
    --region $AWS_REGION

aws secretsmanager create-secret \
    --name "$PROJECT_NAME/aws-secret-key-new" \
    --description "AWS Secret Access Key for Agri IoT application" \
    --secret-string "$AWS_SECRET_ACCESS_KEY" \
    --region $AWS_REGION

# 4. メール設定を作成
echo "📧 メール設定を作成中..."
aws secretsmanager create-secret \
    --name "$PROJECT_NAME/email-host-user-new" \
    --description "Email host user for Agri IoT application" \
    --secret-string "${EMAIL_HOST_USER:-kekenzy@gmail.com}" \
    --region $AWS_REGION

aws secretsmanager create-secret \
    --name "$PROJECT_NAME/email-host-password-new" \
    --description "Email host password for Agri IoT application" \
    --secret-string "${EMAIL_HOST_PASSWORD:-your-app-password}" \
    --region $AWS_REGION

echo "✅ すべての機密情報がSecrets Managerに作成されました！"

echo ""
echo "📋 作成されたシークレット:"
echo "- $PROJECT_NAME/database-url-new"
echo "- $PROJECT_NAME/secret-key-new"
echo "- $PROJECT_NAME/aws-access-key-new"
echo "- $PROJECT_NAME/aws-secret-key-new"
echo "- $PROJECT_NAME/email-host-user-new"
echo "- $PROJECT_NAME/email-host-password-new" 