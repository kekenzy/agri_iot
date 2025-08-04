#!/bin/bash

# ECS停止スクリプト
# 使用方法: ./stop_ecs.sh

set -e

# 設定
CLUSTER_NAME="agri-iot-cluster"
SERVICE_NAME="agri-iot-service"
REGION="ap-northeast-1"

echo "🚫 ECSサービスを停止中..."
echo "クラスター: $CLUSTER_NAME"
echo "サービス: $SERVICE_NAME"
echo "リージョン: $REGION"
echo ""

# 現在のサービス状況を確認
echo "📊 現在のサービス状況:"
aws ecs describe-services \
    --cluster $CLUSTER_NAME \
    --services $SERVICE_NAME \
    --region $REGION \
    --query 'services[0].{Status:status,DesiredCount:desiredCount,RunningCount:runningCount,PendingCount:pendingCount}' \
    --output table

echo ""

# サービスを停止（DesiredCountを0に設定）
echo "⏹️  サービスを停止中..."
aws ecs update-service \
    --cluster $CLUSTER_NAME \
    --service $SERVICE_NAME \
    --desired-count 0 \
    --region $REGION

echo "✅ サービス停止コマンドを実行しました"
echo ""

# 停止完了まで待機
echo "⏳ タスクの停止完了を待機中..."
while true; do
    RUNNING_COUNT=$(aws ecs describe-services \
        --cluster $CLUSTER_NAME \
        --services $SERVICE_NAME \
        --region $REGION \
        --query 'services[0].runningCount' \
        --output text)
    
    if [ "$RUNNING_COUNT" -eq 0 ]; then
        break
    fi
    
    echo "  実行中タスク数: $RUNNING_COUNT"
    sleep 10
done

echo ""

# 最終確認
echo "📊 最終確認:"
aws ecs describe-services \
    --cluster $CLUSTER_NAME \
    --services $SERVICE_NAME \
    --region $REGION \
    --query 'services[0].{Status:status,DesiredCount:desiredCount,RunningCount:runningCount,PendingCount:pendingCount}' \
    --output table

echo ""
echo "🎉 ECSサービスの停止が完了しました！"
echo ""
echo "💡 サービスを再開する場合は以下を実行してください:"
echo "   ./scripts/start_ecs.sh" 