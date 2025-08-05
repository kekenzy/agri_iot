#!/bin/bash

# AWS Secrets Manager更新スクリプト
set -e

# 設定
AWS_REGION="ap-northeast-1"
PROJECT_NAME="agri-iot"

echo "🔐 AWS Secrets Managerの機密情報を更新します..."

# 環境変数の確認
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ] || [ -z "$DB_PASSWORD" ]; then
    echo "❌ 必要な環境変数が設定されていません"
    echo "AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, DB_PASSWORD を設定してください"
    exit 1
fi

# 1. データベース接続情報を更新
echo "📊 データベース接続情報を更新中..."
aws secretsmanager update-secret \
    --secret-id "$PROJECT_NAME/database-url" \
    --secret-string "{\"url\":\"postgresql://agri_user:${DB_PASSWORD}@agri-iot-db.ceswvgqkwv57.ap-northeast-1.rds.amazonaws.com:5432/agri_db\"}" \
    --region $AWS_REGION

# 2. Django SECRET_KEYを更新
echo "🔑 Django SECRET_KEYを更新中..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
aws secretsmanager update-secret \
    --secret-id "$PROJECT_NAME/secret-key" \
    --secret-string "$SECRET_KEY" \
    --region $AWS_REGION

# 3. AWS認証情報を更新
echo "🔑 AWS認証情報を更新中..."
aws secretsmanager update-secret \
    --secret-id "$PROJECT_NAME/aws-access-key" \
    --secret-string "$AWS_ACCESS_KEY_ID" \
    --region $AWS_REGION

aws secretsmanager update-secret \
    --secret-id "$PROJECT_NAME/aws-secret-key" \
    --secret-string "$AWS_SECRET_ACCESS_KEY" \
    --region $AWS_REGION

# 4. メール設定を更新
echo "📧 メール設定を更新中..."
aws secretsmanager update-secret \
    --secret-id "$PROJECT_NAME/email-host-user" \
    --secret-string "${EMAIL_HOST_USER:-kekenzy@gmail.com}" \
    --region $AWS_REGION

aws secretsmanager update-secret \
    --secret-id "$PROJECT_NAME/email-host-password" \
    --secret-string "${EMAIL_HOST_PASSWORD:-your-app-password}" \
    --region $AWS_REGION

echo "✅ すべての機密情報がSecrets Managerに更新されました！"

echo ""
echo "📋 更新されたシークレット:"
echo "- $PROJECT_NAME/database-url"
echo "- $PROJECT_NAME/secret-key"
echo "- $PROJECT_NAME/aws-access-key"
echo "- $PROJECT_NAME/aws-secret-key"
echo "- $PROJECT_NAME/email-host-user"
echo "- $PROJECT_NAME/email-host-password" 