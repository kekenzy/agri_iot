#!/bin/bash

# ECS開始スクリプト
# 使用方法: ./start_ecs.sh [タスク数]

set -e

# 設定
CLUSTER_NAME="agri-iot-cluster"
SERVICE_NAME="agri-iot-service"
REGION="ap-northeast-1"

# デフォルトのタスク数（引数が指定されていない場合）
DEFAULT_DESIRED_COUNT=2
DESIRED_COUNT=${1:-$DEFAULT_DESIRED_COUNT}

echo "🚀 ECSサービスを開始中..."
echo "クラスター: $CLUSTER_NAME"
echo "サービス: $SERVICE_NAME"
echo "リージョン: $REGION"
echo "タスク数: $DESIRED_COUNT"
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

# サービスを開始（DesiredCountを指定した数に設定）
echo "▶️  サービスを開始中..."
aws ecs update-service \
    --cluster $CLUSTER_NAME \
    --service $SERVICE_NAME \
    --desired-count $DESIRED_COUNT \
    --region $REGION

echo "✅ サービス開始コマンドを実行しました"
echo ""

# 起動完了まで待機
echo "⏳ タスクの起動完了を待機中..."
while true; do
    RUNNING_COUNT=$(aws ecs describe-services \
        --cluster $CLUSTER_NAME \
        --services $SERVICE_NAME \
        --region $REGION \
        --query 'services[0].runningCount' \
        --output text)
    
    if [ "$RUNNING_COUNT" -eq "$DESIRED_COUNT" ]; then
        break
    fi
    
    echo "  実行中タスク数: $RUNNING_COUNT / $DESIRED_COUNT"
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

# ヘルスチェック
echo "🏥 ヘルスチェック実行中..."
ALB_DNS=$(aws elbv2 describe-load-balancers \
    --region $REGION \
    --query 'LoadBalancers[?contains(LoadBalancerName, `agri-iot-alb`)].DNSName' \
    --output text)

if [ -n "$ALB_DNS" ]; then
    echo "ALB DNS: $ALB_DNS"
    if curl -f "http://$ALB_DNS/health/" > /dev/null 2>&1; then
        echo "✅ ヘルスチェック成功"
    else
        echo "⚠️  ヘルスチェック失敗（アプリケーションがまだ起動中かもしれません）"
    fi
else
    echo "⚠️  ALB DNSが見つかりません"
fi

echo ""
echo "🎉 ECSサービスの開始が完了しました！"
echo ""
echo "💡 サービスを停止する場合は以下を実行してください:"
echo "   ./scripts/stop_ecs.sh" 