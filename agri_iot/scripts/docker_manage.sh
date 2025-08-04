#!/bin/bash

# Docker環境での管理コマンド用スクリプト

case "$1" in
    "start")
        echo "🚀 アプリケーションを起動中..."
        docker-compose up -d
        ;;
    "stop")
        echo "🛑 アプリケーションを停止中..."
        docker-compose down
        ;;
    "restart")
        echo "🔄 アプリケーションを再起動中..."
        docker-compose restart
        ;;
    "build")
        echo "🔨 イメージを再ビルド中..."
        docker-compose build
        ;;
    "logs")
        echo "📋 ログを表示中..."
        docker-compose logs -f agri_iot
        ;;
    "migrate")
        echo "🗄️ マイグレーションを実行中..."
        docker-compose exec agri_iot python3 manage.py migrate
        ;;
    "makemigrations")
        echo "📝 マイグレーションファイルを作成中..."
        docker-compose exec agri_iot python3 manage.py makemigrations
        ;;
    "shell")
        echo "🐚 Djangoシェルを起動中..."
        docker-compose exec agri_iot python3 manage.py shell
        ;;
    "createsuperuser")
        echo "👤 スーパーユーザーを作成中..."
        docker-compose exec agri_iot python3 manage.py createsuperuser
        ;;
    "loaddata")
        echo "📊 初期データを投入中..."
        docker-compose exec agri_iot python3 manage.py loaddata agri_app/model/yaml/testdata/01_initial.yaml
        docker-compose exec agri_iot python3 manage.py loaddata agri_app/model/yaml/testdata/email_settings_initial.yaml
        ;;
    "test")
        echo "🧪 テストを実行中..."
        docker-compose exec agri_iot python3 manage.py test
        ;;
    "status")
        echo "📊 コンテナの状態を確認中..."
        docker-compose ps
        ;;
    "clean")
        echo "🧹 コンテナとボリュームを削除中..."
        docker-compose down -v
        docker system prune -f
        ;;
    *)
        echo "使用方法: $0 {start|stop|restart|build|logs|migrate|makemigrations|shell|createsuperuser|loaddata|test|status|clean}"
        echo ""
        echo "コマンド一覧:"
        echo "  start           - アプリケーションを起動"
        echo "  stop            - アプリケーションを停止"
        echo "  restart         - アプリケーションを再起動"
        echo "  build           - イメージを再ビルド"
        echo "  logs            - ログを表示"
        echo "  migrate         - マイグレーションを実行"
        echo "  makemigrations  - マイグレーションファイルを作成"
        echo "  shell           - Djangoシェルを起動"
        echo "  createsuperuser - スーパーユーザーを作成"
        echo "  loaddata        - 初期データを投入"
        echo "  test            - テストを実行"
        echo "  status          - コンテナの状態を確認"
        echo "  clean           - コンテナとボリュームを削除"
        exit 1
        ;;
esac 