#!/bin/bash

# AWSデプロイスクリプト（既存イメージ使用）
set -e

# 設定
AWS_REGION="ap-northeast-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPOSITORY="agri-iot"
ECS_CLUSTER="agri-iot-cluster"
ECS_SERVICE="agri-iot-service"
TASK_DEFINITION="agri-iot-app"

echo "🚀 AWS ECS デプロイを開始します（既存イメージ使用）..."

# 1. ECRリポジトリの確認
echo "📦 ECRリポジトリを確認中..."
aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $AWS_REGION

# 2. 最新のイメージを確認
echo "🔍 最新のイメージを確認中..."
aws ecr describe-images --repository-name $ECR_REPOSITORY --region $AWS_REGION --query 'imageDetails[*].[imageTags[0],imagePushedAt]' --output table

# 3. 強制デプロイを実行
echo "🔄 強制デプロイを実行中..."
aws ecs update-service \
    --cluster $ECS_CLUSTER \
    --service $ECS_SERVICE \
    --force-new-deployment \
    --region $AWS_REGION

# 4. デプロイメントの完了を待つ
echo "⏳ デプロイメントの完了を待機中..."
aws ecs wait services-stable \
    --cluster $ECS_CLUSTER \
    --services $ECS_SERVICE \
    --region $AWS_REGION

echo "✅ デプロイが完了しました！"
echo ""
echo "🌐 アプリケーションURL: http://agri-iot-alb-1112589158.ap-northeast-1.elb.amazonaws.com"
echo "📊 ECSコンソール: https://console.aws.amazon.com/ecs/home?region=$AWS_REGION#/clusters/$ECS_CLUSTER"
echo "📋 ログ確認: aws logs tail /ecs/agri-iot-app --follow"
echo "🏥 ヘルスチェック: curl http://agri-iot-alb-1112589158.ap-northeast-1.elb.amazonaws.com/health/" 