#!/bin/bash

# AWS認証情報設定スクリプト
echo "🔐 AWS認証情報を設定します..."

# AWS CLIの設定
aws configure set aws_access_key_id AKIAWNHBWGAAVHMPGRL5
aws configure set aws_secret_access_key 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
aws configure set default.region ap-northeast-1
aws configure set default.output json

echo "✅ AWS認証情報が設定されました！"

# アカウント情報の確認
echo "📋 AWSアカウント情報を確認中..."
aws sts get-caller-identity

echo ""
echo "🚀 次のステップ:"
echo "1. cd aws/terraform"
echo "2. terraform init"
echo "3. terraform plan"
echo "4. terraform apply" 