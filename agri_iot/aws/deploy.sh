#!/bin/bash

# AWSデプロイスクリプト（Dockerベース）
set -e

# 設定
AWS_REGION="ap-northeast-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPOSITORY="agri-iot"
ECS_CLUSTER="agri-iot-cluster"
ECS_SERVICE="agri-iot-service"
TASK_DEFINITION="agri-iot-app"

echo "🚀 AWS ECS デプロイを開始します（Dockerベース）..."

# 1. ECRリポジトリの作成（存在しない場合）
echo "📦 ECRリポジトリを確認中..."
aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $AWS_REGION 2>/dev/null || {
    echo "ECRリポジトリを作成中..."
    aws ecr create-repository --repository-name $ECR_REPOSITORY --region $AWS_REGION
}

# 2. ECRにログイン
echo "🔐 ECRにログイン中..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# 3. Dockerイメージのビルド（本番環境用）
echo "🔨 Dockerイメージをビルド中..."
cd ..
docker build -f agri_iot/Dockerfile -t $ECR_REPOSITORY:latest agri_iot/

# 4. イメージにタグを付ける
echo "🏷️ イメージにタグを付ける中..."
docker tag $ECR_REPOSITORY:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest

# 5. ECRにプッシュ
echo "📤 ECRにプッシュ中..."
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:latest

# 6. タスク定義の更新
echo "📝 タスク定義を更新中..."
aws ecs register-task-definition \
    --cli-input-json file://agri_iot/aws/ecs-task-definition.json \
    --region $AWS_REGION

# 7. サービスの更新
echo "🔄 サービスを更新中..."
aws ecs update-service \
    --cluster $ECS_CLUSTER \
    --service $ECS_SERVICE \
    --task-definition $TASK_DEFINITION \
    --region $AWS_REGION

# 8. デプロイメントの完了を待つ
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