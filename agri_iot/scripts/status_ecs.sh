#!/bin/bash

# ECS状況確認スクリプト
# 使用方法: ./status_ecs.sh

set -e

# 設定
CLUSTER_NAME="agri-iot-cluster"
SERVICE_NAME="agri-iot-service"
REGION="ap-northeast-1"

echo "📊 ECSサービス状況確認"
echo "クラスター: $CLUSTER_NAME"
echo "サービス: $SERVICE_NAME"
echo "リージョン: $REGION"
echo ""

# サービス詳細情報
echo "🔍 サービス詳細:"
aws ecs describe-services \
    --cluster $CLUSTER_NAME \
    --services $SERVICE_NAME \
    --region $REGION \
    --query 'services[0].{Status:status,DesiredCount:desiredCount,RunningCount:runningCount,PendingCount:pendingCount,TaskDefinition:taskDefinition}' \
    --output table

echo ""

# 実行中タスクの詳細
echo "🔄 実行中タスク:"
TASK_ARNS=$(aws ecs list-tasks \
    --cluster $CLUSTER_NAME \
    --service-name $SERVICE_NAME \
    --region $REGION \
    --query 'taskArns' \
    --output text)

if [ -n "$TASK_ARNS" ]; then
    aws ecs describe-tasks \
        --cluster $CLUSTER_NAME \
        --tasks $TASK_ARNS \
        --region $REGION \
        --query 'tasks[].{TaskArn:taskArn,LastStatus:lastStatus,HealthStatus:healthStatus,CreatedAt:createdAt,StartedAt:startedAt}' \
        --output table
else
    echo "  実行中タスクなし"
fi

echo ""

# 最新のイベント
echo "📝 最新イベント（最新5件）:"
aws ecs describe-services \
    --cluster $CLUSTER_NAME \
    --services $SERVICE_NAME \
    --region $REGION \
    --query 'services[0].events[0:5].{CreatedAt:createdAt,Message:message}' \
    --output table

echo ""

# ALB状況確認
echo "🌐 ALB状況:"
ALB_DNS=$(aws elbv2 describe-load-balancers \
    --region $REGION \
    --query 'LoadBalancers[?contains(LoadBalancerName, `agri-iot-alb`)].DNSName' \
    --output text)

if [ -n "$ALB_DNS" ]; then
    echo "ALB DNS: $ALB_DNS"
    
    # ヘルスチェック
    echo "🏥 ヘルスチェック:"
    if curl -f "http://$ALB_DNS/health/" > /dev/null 2>&1; then
        echo "  ✅ アプリケーション正常応答"
    else
        echo "  ❌ アプリケーション応答なし"
    fi
    
    # メインページチェック
    if curl -f "http://$ALB_DNS/" > /dev/null 2>&1; then
        echo "  ✅ メインページ正常応答"
    else
        echo "  ❌ メインページ応答なし"
    fi
else
    echo "  ALB DNSが見つかりません"
fi

echo ""
echo "💡 コマンド一覧:"
echo "  停止: ./scripts/stop_ecs.sh"
echo "  開始: ./scripts/start_ecs.sh [タスク数]"
echo "  状況: ./scripts/status_ecs.sh" 