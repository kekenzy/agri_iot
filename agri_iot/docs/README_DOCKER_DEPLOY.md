# Dockerベース AWS ECS デプロイガイド

このプロジェクトは、venvを使わずにDockerベースでAWS ECSにデプロイするように設定されています。

## 🏗️ アーキテクチャ

- **コンテナ**: Python 3.11.3-slim-bullseye
- **Webサーバー**: Gunicorn
- **静的ファイル**: WhiteNoise + S3
- **データベース**: PostgreSQL (RDS)
- **キャッシュ**: Redis (ElastiCache)
- **ロードバランサー**: ALB
- **コンテナオーケストレーション**: ECS Fargate

## 🚀 デプロイ手順

### 1. 前提条件

- AWS CLI が設定済み
- Docker がインストール済み
- 必要なAWSリソースが作成済み（ECS、RDS、S3、ALB等）

### 2. ローカル開発

```bash
# 開発環境の起動
docker-compose up --build

# データベースマイグレーション
docker-compose exec agri_iot python manage.py migrate

# 初期データの投入
docker-compose exec agri_iot python manage.py loaddata agri_app/model/yaml/testdata/01_initial.yaml
```

### 3. AWS ECS デプロイ

```bash
# 通常デプロイ
cd agri_iot/aws
./deploy.sh

# 完全デプロイ（クリーンアップ含む）
cd agri_iot/aws
./deploy-full.sh
```

## 📁 ファイル構成

```
agri_iot/
├── Dockerfile                 # 本番環境用Dockerfile
├── requirements.in           # 依存関係定義
├── requirements.txt          # 固定バージョン依存関係
├── .dockerignore            # Dockerビルド除外ファイル
├── agri_iot/
│   ├── settings/
│   │   ├── base.py          # 基本設定
│   │   ├── local.py         # 開発環境設定
│   │   └── production.py    # 本番環境設定
│   └── urls.py              # URL設定（ヘルスチェック含む）
└── aws/
    ├── deploy.sh            # 通常デプロイスクリプト
    ├── deploy-full.sh       # 完全デプロイスクリプト
    └── ecs-task-definition.json  # ECSタスク定義
```

## 🔧 設定

### 環境変数

本番環境では以下の環境変数が設定されます：

- `DJANGO_SETTINGS_MODULE`: `agri_iot.settings.production`
- `DATABASE_URL`: RDS接続情報
- `AWS_ACCESS_KEY_ID`: S3アクセスキー
- `AWS_SECRET_ACCESS_KEY`: S3シークレットキー
- `AWS_STORAGE_BUCKET_NAME`: S3バケット名
- `SECRET_KEY`: Django秘密鍵

### ヘルスチェック

- エンドポイント: `/health/`
- チェック間隔: 30秒
- タイムアウト: 5秒
- リトライ回数: 3回

## 📊 監視・ログ

### CloudWatch ログ

```bash
# ログの確認
aws logs tail /ecs/agri-iot-app --follow
```

### ヘルスチェック

```bash
# ヘルスチェック
curl http://agri-iot-alb-1112589158.ap-northeast-1.elb.amazonaws.com/health/
```

## 🔍 トラブルシューティング

### よくある問題

1. **400エラー**: ヘルスチェックで400エラーが発生
   - 設定ファイルの確認
   - データベース接続の確認
   - 静的ファイルの設定確認

2. **コンテナ起動失敗**: 
   - ログの確認: `aws logs tail /ecs/agri-iot-app --follow`
   - 環境変数の確認
   - 依存関係の確認

3. **静的ファイルが表示されない**:
   - S3バケットの設定確認
   - WhiteNoiseの設定確認

### デバッグ手順

1. ECSタスクのログを確認
2. ヘルスチェックエンドポイントにアクセス
3. データベース接続を確認
4. 環境変数を確認

## 🌐 アクセス情報

- **アプリケーションURL**: http://agri-iot-alb-1112589158.ap-northeast-1.elb.amazonaws.com
- **ヘルスチェック**: http://agri-iot-alb-1112589158.ap-northeast-1.elb.amazonaws.com/health/
- **ECSコンソール**: https://console.aws.amazon.com/ecs/home?region=ap-northeast-1#/clusters/agri-iot-cluster

## 📝 注意事項

- venvディレクトリは削除済み（Dockerコンテナ内で依存関係を管理）
- 本番環境では`agri_iot.settings.production`を使用
- 静的ファイルはS3またはWhiteNoiseで配信
- ヘルスチェックエンドポイントが追加済み 