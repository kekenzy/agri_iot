#!/bin/bash

echo "🚀 Docker環境でアプリケーションを起動します..."

# 既存のコンテナを停止・削除
echo "📦 既存のコンテナを停止・削除中..."
docker-compose down

# イメージを再ビルド
echo "🔨 Dockerイメージを再ビルド中..."
docker-compose build

# コンテナを起動
echo "🚀 コンテナを起動中..."
docker-compose up -d

# データベースの準備ができるまで待機
echo "⏳ データベースの準備を待機中..."
sleep 10

# マイグレーションを実行
echo "🗄️ データベースマイグレーションを実行中..."
docker-compose exec agri_iot python3 manage.py migrate

# 初期データを投入
echo "📊 初期データを投入中..."
docker-compose exec agri_iot python3 manage.py loaddata agri_app/model/yaml/testdata/01_initial.yaml
docker-compose exec agri_iot python3 manage.py loaddata agri_app/model/yaml/testdata/email_settings_initial.yaml

# スーパーユーザーを作成（必要に応じて）
echo "👤 スーパーユーザーを作成しますか？ (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    docker-compose exec agri_iot python3 manage.py createsuperuser
fi

echo "✅ アプリケーションの起動が完了しました！"
echo ""
echo "🌐 アプリケーション: http://localhost:8000"
echo "📧 メールサーバー: http://localhost:8025"
echo "🗄️ データベース管理: http://localhost:8080"
echo ""
echo "📋 ログを確認するには: docker-compose logs -f agri_iot"
echo "🛑 停止するには: docker-compose down" 