# AWSデプロイ クイックスタートガイド

## 🚀 ワンクリックデプロイ

あなたのAWSアカウント情報を使用して、以下のコマンドでワンクリックデプロイが可能です：

```bash
# 1. AWS認証情報を設定
./aws/setup-aws.sh

# 2. 完全なデプロイを実行
./aws/deploy-full.sh
```

## 📋 アカウント情報

- **アカウントID**: 440707461121
- **ユーザー名**: kenzy
- **リージョン**: ap-northeast-1 (東京)

## 🔧 手動デプロイ手順

### 1. 前提条件の確認

```bash
# AWS CLIの確認
aws --version

# Dockerの確認
docker --version

# Terraformの確認
terraform --version
```

### 2. AWS認証情報の設定

```bash
# 自動設定
./aws/setup-aws.sh

# または手動設定
aws configure set aws_access_key_id AKIAWNHBWGAAVHMPGRL5
aws configure set aws_secret_access_key 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
aws configure set default.region ap-northeast-1
aws configure set default.output json
```

### 3. インフラストラクチャの構築

```bash
cd aws/terraform
terraform init
terraform plan
terraform apply
```

### 4. アプリケーションのデプロイ

```bash
# プロジェクトルートに戻る
cd ../..

# デプロイ実行
./aws/deploy.sh
```

## 🌐 アクセス情報

デプロイ完了後、以下のURLでアクセスできます：

- **ALB URL**: `http://agri-iot-alb-xxxxxxxxx.ap-northeast-1.elb.amazonaws.com`
- **ECSコンソール**: https://console.aws.amazon.com/ecs/home?region=ap-northeast-1
- **RDSコンソール**: https://console.aws.amazon.com/rds/home?region=ap-northeast-1
- **S3コンソール**: https://console.aws.amazon.com/s3/buckets?region=ap-northeast-1

## 📊 監視とログ

```bash
# アプリケーションログの確認
aws logs tail /ecs/agri-iot-app --follow

# ECSサービスの状態確認
aws ecs describe-services --cluster agri-iot-cluster --services agri-iot-service

# ALBのターゲットヘルス確認
aws elbv2 describe-target-health --target-group-arn arn:aws:elasticloadbalancing:ap-northeast-1:440707461121:targetgroup/agri-iot-tg/ID
```

## 🔒 セキュリティ設定

### Secrets Manager

以下の機密情報が自動的にSecrets Managerに保存されます：

- データベース接続情報
- Django SECRET_KEY
- AWS認証情報
- メール設定

### IAMロール

- **ECS Task Execution Role**: コンテナ起動用
- **ECS Task Role**: アプリケーション実行用

## 💰 コスト見積もり

月間の概算コスト（東京リージョン）：

- **ECS Fargate**: ~$30-50/月
- **RDS PostgreSQL**: ~$25-40/月
- **ALB**: ~$20/月
- **S3**: ~$5-10/月
- **CloudWatch**: ~$5-10/月

**合計**: ~$85-130/月

## 🛠️ トラブルシューティング

### よくある問題

1. **権限エラー**
   ```bash
   # IAMロールの確認
   aws iam get-role --role-name ecsTaskExecutionRole
   ```

2. **コンテナ起動エラー**
   ```bash
   # タスクの詳細確認
   aws ecs describe-tasks --cluster agri-iot-cluster --tasks task-id
   ```

3. **データベース接続エラー**
   ```bash
   # RDSの状態確認
   aws rds describe-db-instances --db-instance-identifier agri-iot-db
   ```

### ログの確認

```bash
# リアルタイムログ
aws logs tail /ecs/agri-iot-app --follow

# 特定の時間のログ
aws logs filter-log-events \
    --log-group-name /ecs/agri-iot-app \
    --start-time 1640995200000 \
    --end-time 1641081600000
```

## 🔄 更新手順

アプリケーションの更新時：

```bash
# 1. コードを更新

# 2. 新しいイメージをビルド・プッシュ
./aws/deploy.sh

# 3. サービスの更新
aws ecs update-service \
    --cluster agri-iot-cluster \
    --service agri-iot-service \
    --force-new-deployment
```

## 🧹 クリーンアップ

リソースを削除する場合：

```bash
# Terraformでリソースを削除
cd aws/terraform
terraform destroy

# ECRリポジトリの削除
aws ecr delete-repository --repository-name agri-iot --force

# Secrets Managerの削除
aws secretsmanager delete-secret --secret-id agri-iot/database-url --force-deletion-without-recovery
aws secretsmanager delete-secret --secret-id agri-iot/secret-key --force-deletion-without-recovery
# ... 他のシークレットも同様に削除
```

## 📞 サポート

問題が発生した場合は、以下を確認してください：

1. CloudWatchログ
2. ECSタスクの状態
3. ALBのターゲットヘルス
4. RDSの接続状態
5. IAMロールの権限

詳細なエラーメッセージがあれば、より具体的な解決策を提供できます。 