# Docker環境でのアプリケーション実行

このドキュメントでは、Docker環境でアプリケーションを実行する方法を説明します。

## 🚀 クイックスタート

### 1. 初回セットアップ

```bash
# アプリケーションを起動（初回は自動的にビルドとマイグレーションが実行されます）
./start_docker.sh
```

### 2. 基本的な操作

```bash
# アプリケーションを起動
./docker_manage.sh start

# アプリケーションを停止
./docker_manage.sh stop

# アプリケーションを再起動
./docker_manage.sh restart

# ログを確認
./docker_manage.sh logs

# コンテナの状態を確認
./docker_manage.sh status
```

## 📋 利用可能なサービス

| サービス | URL | 説明 |
|---------|-----|------|
| アプリケーション | http://localhost:8000 | メインのWebアプリケーション |
| メールサーバー | http://localhost:8025 | MailHog（開発用メールサーバー） |
| データベース管理 | http://localhost:8080 | pgAdmin（PostgreSQL管理ツール） |

## 🔧 管理コマンド

### データベース関連

```bash
# マイグレーションを実行
./docker_manage.sh migrate

# マイグレーションファイルを作成
./docker_manage.sh makemigrations

# 初期データを投入
./docker_manage.sh loaddata
```

### ユーザー管理

```bash
# スーパーユーザーを作成
./docker_manage.sh createsuperuser

# Djangoシェルを起動
./docker_manage.sh shell
```

### 開発・テスト

```bash
# イメージを再ビルド
./docker_manage.sh build

# テストを実行
./docker_manage.sh test
```

### メンテナンス

```bash
# コンテナとボリュームを削除（データが消去されます）
./docker_manage.sh clean
```

## 📧 メール送信機能

### メール送信設定

アプリケーションには以下のメール送信機能が含まれています：

1. **お知らせメール送信**
   - お知らせ作成時に自動送信
   - 手動送信機能
   - 送信状況の管理

2. **メール送信設定管理**
   - デフォルト送信設定
   - 件名テンプレート
   - 送信者名の設定

### メール送信の確認

開発環境では、送信されたメールはMailHogで確認できます：

1. アプリケーションでメール送信を実行
2. http://localhost:8025 にアクセス
3. 送信されたメールを確認

## 🗄️ データベース

### PostgreSQL設定

- **ホスト**: localhost
- **ポート**: 5432
- **データベース**: agri_db
- **ユーザー**: agri_user
- **パスワード**: agri_password

### pgAdminでの管理

1. http://localhost:8080 にアクセス
2. ログイン情報：
   - Email: example@example.com
   - Password: password
3. サーバー接続情報：
   - Host: db
   - Port: 5432
   - Database: agri_db
   - Username: agri_user
   - Password: agri_password

## 🔍 トラブルシューティング

### よくある問題

1. **ポートが既に使用されている**
   ```bash
   # 使用中のポートを確認
   lsof -i :8000
   lsof -i :8025
   lsof -i :8080
   ```

2. **コンテナが起動しない**
   ```bash
   # ログを確認
   ./docker_manage.sh logs
   
   # コンテナの状態を確認
   ./docker_manage.sh status
   ```

3. **データベース接続エラー**
   ```bash
   # データベースコンテナを再起動
   docker-compose restart db
   
   # マイグレーションを再実行
   ./docker_manage.sh migrate
   ```

### ログの確認

```bash
# 全サービスのログ
docker-compose logs

# 特定サービスのログ
docker-compose logs agri_iot
docker-compose logs db
docker-compose logs mailhog
```

## 📁 ファイル構成

```
agri_iot/
├── start_docker.sh          # 初回セットアップスクリプト
├── docker_manage.sh         # 管理コマンドスクリプト
├── docker-compose.yml       # Docker Compose設定
├── Dockerfile              # アプリケーション用Dockerfile
└── agri_iot_www/
    └── Dockerfile          # Webサーバー用Dockerfile
```

## 🔄 更新手順

アプリケーションのコードを更新した場合：

```bash
# 1. イメージを再ビルド
./docker_manage.sh build

# 2. アプリケーションを再起動
./docker_manage.sh restart

# 3. 必要に応じてマイグレーションを実行
./docker_manage.sh migrate
```

## 🧹 クリーンアップ

完全に環境をクリーンアップする場合：

```bash
# コンテナ、ボリューム、イメージを削除
./docker_manage.sh clean
```

**注意**: このコマンドを実行すると、データベースのデータがすべて削除されます。 