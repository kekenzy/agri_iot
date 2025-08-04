# Scripts Directory

このディレクトリには、Djangoアプリケーションの管理用スクリプトが含まれています。

## 管理ユーザー関連スクリプト

### 1. Adminユーザー作成スクリプト

#### `create_admin.py`
- **説明**: Django管理コマンドを使用してadminユーザーを作成
- **使用方法**: `python manage.py create_admin`
- **引数**: 
  - `--username`: ユーザー名（デフォルト: admin）
  - `--email`: メールアドレス（デフォルト: admin@agri-iot.com）
  - `--password`: パスワード（デフォルト: Kekenji1）

#### `create_admin_simple.py`
- **説明**: シンプルなadminユーザー作成スクリプト
- **使用方法**: `python scripts/create_admin_simple.py`

#### `create_admin_direct.py`
- **説明**: データベースに直接接続してadminユーザーを作成
- **使用方法**: `python scripts/create_admin_direct.py`

#### `create_admin_script.py`
- **説明**: スクリプト形式のadminユーザー作成
- **使用方法**: `python scripts/create_admin_script.py`

### 2. パスワード変更スクリプト

#### `change_admin_password.py`
- **説明**: Django管理コマンドを使用してadminユーザーのパスワードを変更
- **使用方法**: `python manage.py change_admin_password`
- **引数**:
  - `--username`: ユーザー名（デフォルト: admin）
  - `--password`: 新しいパスワード（デフォルト: Kekenji1）

#### `change_admin_password.sh`
- **説明**: シェルスクリプト版のパスワード変更
- **使用方法**: `./scripts/change_admin_password.sh`

## Docker関連スクリプト

### `docker_manage.sh`
- **説明**: Dockerコンテナの管理スクリプト
- **使用方法**: `./scripts/docker_manage.sh [start|stop|restart|logs|shell]`

### `start_docker.sh`
- **説明**: Dockerコンテナを起動するスクリプト
- **使用方法**: `./scripts/start_docker.sh`

## テスト関連スクリプト

### `test_password.py`
- **説明**: パスワード機能のテストスクリプト
- **使用方法**: `python scripts/test_password.py`

### `test_email.py`
- **説明**: メール機能のテストスクリプト
- **使用方法**: `python scripts/test_email.py`

## AWS関連スクリプト

### `get_ses_smtp_credentials.py`
- **説明**: AWS SESのSMTP認証情報を取得するスクリプト
- **使用方法**: `python scripts/get_ses_smtp_credentials.py`

## ECS管理スクリプト

### `stop_ecs.sh`
- **説明**: ECSサービスを停止するスクリプト
- **使用方法**: `./scripts/stop_ecs.sh`
- **機能**: 
  - 現在のサービス状況を表示
  - DesiredCountを0に設定してサービスを停止
  - タスクの停止完了まで待機
  - 最終確認を実行

### `start_ecs.sh`
- **説明**: ECSサービスを開始するスクリプト
- **使用方法**: `./scripts/start_ecs.sh [タスク数]`
- **引数**: 
  - `タスク数`: 起動するタスク数（デフォルト: 2）
- **機能**:
  - 現在のサービス状況を表示
  - 指定したタスク数でサービスを開始
  - タスクの起動完了まで待機
  - ヘルスチェックを実行
  - 最終確認を実行

### `status_ecs.sh`
- **説明**: ECSサービスの状況を確認するスクリプト
- **使用方法**: `./scripts/status_ecs.sh`
- **機能**:
  - サービス詳細情報の表示
  - 実行中タスクの詳細表示
  - 最新イベントの表示
  - ALB状況とヘルスチェック
  - アプリケーション応答確認

## 自動再起動設定

ECSの自動再起動機能は現在**無効**に設定されています：

- **Deployment Circuit Breaker**: 有効
- **Maximum Percent**: 100%
- **Minimum Healthy Percent**: 0%
- **Rollback**: 有効

これにより、タスクが失敗しても自動的に新しいタスクで置き換えられません。
手動でサービスを再開する場合は `./scripts/start_ecs.sh` を使用してください。

## 使用例

### Adminユーザーの作成
```bash
# Django管理コマンドを使用
python manage.py create_admin --username admin --password Kekenji1

# スクリプトを使用
python scripts/create_admin_simple.py
```

### パスワードの変更
```bash
# Django管理コマンドを使用
python manage.py change_admin_password --username admin --password NewPassword123

# シェルスクリプトを使用
./scripts/change_admin_password.sh
```

### Dockerコンテナの管理
```bash
# コンテナを起動
./scripts/start_docker.sh

# コンテナを管理
./scripts/docker_manage.sh start
./scripts/docker_manage.sh stop
./scripts/docker_manage.sh restart
```

### ECSサービスの管理
```bash
# サービス状況確認
./scripts/status_ecs.sh

# サービス停止
./scripts/stop_ecs.sh

# サービス開始（デフォルト2タスク）
./scripts/start_ecs.sh

# サービス開始（1タスクで起動）
./scripts/start_ecs.sh 1

# サービス開始（4タスクで起動）
./scripts/start_ecs.sh 4
```

## 注意事項

- スクリプトを実行する前に、適切な権限があることを確認してください
- 本番環境では、セキュリティを考慮してパスワードを変更してください
- データベースに直接接続するスクリプトは、開発環境でのみ使用してください 