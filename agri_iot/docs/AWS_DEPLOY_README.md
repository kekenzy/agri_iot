# AWS ECS デプロイガイド

このドキュメントでは、農業IoTアプリケーションをAWS ECS（Elastic Container Service）にデプロイする方法を説明します。

## 🏗️ アーキテクチャ概要

```
Internet → ALB → ECS Fargate → RDS PostgreSQL
                ↓
            S3 (Static/Media)
                ↓
            CloudWatch Logs
```

### 使用するAWSサービス

- **ECS Fargate**: コンテナオーケストレーション
- **RDS PostgreSQL**: データベース
- **Application Load Balancer**: ロードバランサー
- **S3**: 静的ファイル・メディアファイル保存
- **Secrets Manager**: 機密情報管理
- **CloudWatch**: ログ管理
- **Route 53**: DNS管理（オプション）

## 📋 前提条件

### 1. AWS CLIの設定

```bash
# AWS CLIのインストール
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# AWS認証情報の設定
aws configure
```

### 2. Terraformのインストール

```bash
# macOS
brew install terraform

# Linux
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
sudo apt-get update && sudo apt-get install terraform
```

### 3. Dockerのインストール

```bash
# macOS
brew install --cask docker

# Linux
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

## 🚀 デプロイ手順

### 1. インフラストラクチャの構築

```bash
# Terraformディレクトリに移動
cd aws/terraform

# Terraformの初期化
terraform init

# 変数ファイルの作成
cat > terraform.tfvars << EOF
aws_region = "ap-northeast-1"
project_name = "agri-iot"
db_password = "your-secure-password"
domain_name = "your-domain.com"
certificate_arn = "arn:aws:acm:region:account:certificate/certificate-id"
EOF

# インフラストラクチャの構築
terraform plan
terraform apply
```

### 2. ECRリポジトリの作成

```bash
# ECRリポジトリの作成
aws ecr create-repository --repository-name agri-iot --region ap-northeast-1
```

### 3. Dockerイメージのビルドとプッシュ

```bash
# プロジェクトルートに戻る
cd ../..

# AWSアカウントIDの取得
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION="ap-northeast-1"

# ECRにログイン
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# イメージのビルド
docker build -f Dockerfile.production -t agri-iot:latest .

# タグ付け
docker tag agri-iot:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/agri-iot:latest

# ECRにプッシュ
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/agri-iot:latest
```

### 4. アプリケーションのデプロイ

```bash
# デプロイスクリプトの実行
chmod +x aws/deploy.sh
./aws/deploy.sh
```

### 5. データベースの初期化

```bash
# ECSタスクを実行してマイグレーション
aws ecs run-task \
    --cluster agri-iot-cluster \
    --task-definition agri-iot-app \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
    --overrides '{"containerOverrides":[{"name":"agri-iot-app","command":["python","manage.py","migrate"]}]}'

# 初期データの投入
aws ecs run-task \
    --cluster agri-iot-cluster \
    --task-definition agri-iot-app \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
    --overrides '{"containerOverrides":[{"name":"agri-iot-app","command":["python","manage.py","loaddata","agri_app/model/yaml/testdata/01_initial.yaml"]}]}'
```

## 🔧 設定ファイルの説明

### 1. 本番環境設定 (`agri_iot/settings/production.py`)

- HTTPS強制リダイレクト
- セキュリティヘッダー設定
- RDS PostgreSQL接続
- S3静的ファイル配信
- CloudWatchログ設定

### 2. Dockerfile (`Dockerfile.production`)

- 軽量なPythonイメージ使用
- 非rootユーザーでの実行
- Gunicornでの本番サーバー起動
- ヘルスチェック対応

### 3. Terraform設定

- **VPC**: パブリック・プライベートサブネット
- **RDS**: PostgreSQLデータベース
- **ECS**: Fargateクラスターとサービス
- **ALB**: ロードバランサー
- **S3**: 静的ファイル・メディア保存
- **Secrets Manager**: 機密情報管理

## 📊 監視とログ

### CloudWatchログの確認

```bash
# ログの確認
aws logs tail /ecs/agri-iot-app --follow

# ロググループの一覧
aws logs describe-log-groups
```

### メトリクスの確認

```bash
# ECSサービスの状態確認
aws ecs describe-services --cluster agri-iot-cluster --services agri-iot-service

# ALBのターゲットヘルス確認
aws elbv2 describe-target-health --target-group-arn arn:aws:elasticloadbalancing:...
```

## 🔒 セキュリティ設定

### 1. Secrets Manager

以下の機密情報をSecrets Managerで管理：

- データベース接続情報
- Django SECRET_KEY
- AWS認証情報
- メール設定

### 2. IAMロール

- **ECS Task Execution Role**: コンテナ起動用
- **ECS Task Role**: アプリケーション実行用

### 3. セキュリティグループ

- **ALB**: HTTP/HTTPSのみ許可
- **ECS**: ALBからの8000番ポートのみ許可
- **RDS**: ECSからの5432番ポートのみ許可

## 🔄 CI/CDパイプライン

### GitHub Actions設定例

```yaml
name: Deploy to AWS ECS

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v1
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ap-northeast-1
    
    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v1
    
    - name: Build, tag, and push image to Amazon ECR
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        ECR_REPOSITORY: agri-iot
        IMAGE_TAG: latest
      run: |
        docker build -f Dockerfile.production -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
    
    - name: Deploy to ECS
      run: |
        aws ecs update-service --cluster agri-iot-cluster --service agri-iot-service --force-new-deployment
```

## 🛠️ トラブルシューティング

### よくある問題

1. **コンテナが起動しない**
   ```bash
   # タスクの詳細を確認
   aws ecs describe-tasks --cluster agri-iot-cluster --tasks task-id
   
   # ログを確認
   aws logs tail /ecs/agri-iot-app --follow
   ```

2. **データベース接続エラー**
   ```bash
   # RDSの状態確認
   aws rds describe-db-instances --db-instance-identifier agri-iot-db
   
   # セキュリティグループの確認
   aws ec2 describe-security-groups --group-ids sg-xxx
   ```

3. **静的ファイルが表示されない**
   ```bash
   # S3バケットの確認
   aws s3 ls s3://agri-iot-static/
   
   # バケットポリシーの確認
   aws s3api get-bucket-policy --bucket agri-iot-static
   ```

### ログの確認方法

```bash
# ECSタスクのログ
aws logs tail /ecs/agri-iot-app --follow

# ALBのアクセスログ
aws logs tail /aws/applicationloadbalancer/agri-iot-alb --follow

# RDSのログ
aws rds describe-db-log-files --db-instance-identifier agri-iot-db
```

## 💰 コスト最適化

### 推奨設定

1. **RDS**: 開発時は`db.t3.micro`、本番時は`db.t3.small`以上
2. **ECS**: 必要に応じてAuto Scaling設定
3. **S3**: ライフサイクルポリシーで古いファイルを削除
4. **CloudWatch**: ログ保持期間を30日程度に設定

### コスト監視

```bash
# 月間コストの確認
aws ce get-cost-and-usage \
    --time-period Start=2024-01-01,End=2024-01-31 \
    --granularity MONTHLY \
    --metrics BlendedCost
```

## 🧹 クリーンアップ

### リソースの削除

```bash
# Terraformでリソースを削除
cd aws/terraform
terraform destroy

# ECRリポジトリの削除
aws ecr delete-repository --repository-name agri-iot --force

# 手動で削除が必要なリソース
# - S3バケット内のファイル
# - CloudWatchロググループ
# - Secrets Managerのシークレット
```

## 📞 サポート

問題が発生した場合は、以下を確認してください：

1. CloudWatchログ
2. ECSタスクの状態
3. ALBのターゲットヘルス
4. RDSの接続状態
5. S3バケットのアクセス権限

詳細なログやエラーメッセージがあれば、より具体的な解決策を提供できます。 