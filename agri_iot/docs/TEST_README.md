# Docker上でのテスト実行ガイド

このガイドでは、Docker環境でAgri IoTアプリケーションのテストを実行する方法を説明します。

## 前提条件

- DockerとDocker Composeがインストールされていること
- アプリケーションがDocker上で正常に動作していること

## テスト実行スクリプト

`run_tests.sh`スクリプトを使用して、Docker上でテストを簡単に実行できます。

### 基本的な使用方法

```bash
# ヘルプを表示
./agri_iot/run_tests.sh --help

# 全てのテストを実行
./agri_iot/run_tests.sh --all

# 特定のテストカテゴリを実行
./agri_iot/run_tests.sh --models
./agri_iot/run_tests.sh --views
./agri_iot/run_tests.sh --forms
./agri_iot/run_tests.sh --utils
./agri_iot/run_tests.sh --integration

# カバレッジ付きでテスト実行
./agri_iot/run_tests.sh --all --coverage

# 詳細出力でテスト実行
./agri_iot/run_tests.sh --views --verbose
```

### オプション一覧

| オプション | 説明 |
|-----------|------|
| `--all` | 全てのテストを実行 |
| `--models` | モデルテストのみ実行 |
| `--views` | ビューテストのみ実行 |
| `--forms` | フォームテストのみ実行 |
| `--utils` | ユーティリティテストのみ実行 |
| `--integration` | 統合テストのみ実行 |
| `--coverage` | カバレッジ付きでテスト実行 |
| `--verbose` | 詳細出力でテスト実行 |
| `--help` | ヘルプを表示 |

## 手動でのテスト実行

スクリプトを使用せずに、直接Dockerコマンドでテストを実行することもできます。

### 基本的なテスト実行

```bash
# 全てのテストを実行
docker-compose exec agri_iot python manage.py test agri_app.tests

# 特定のテストファイルを実行
docker-compose exec agri_iot python manage.py test agri_app.tests.test_models
docker-compose exec agri_iot python manage.py test agri_app.tests.test_views
docker-compose exec agri_iot python manage.py test agri_app.tests.test_forms
docker-compose exec agri_iot python manage.py test agri_app.tests.test_utils
docker-compose exec agri_iot python manage.py test agri_app.tests.test_integration

# 特定のテストクラスを実行
docker-compose exec agri_iot python manage.py test agri_app.tests.test_models.UserProfileModelTest

# 特定のテストメソッドを実行
docker-compose exec agri_iot python manage.py test agri_app.tests.test_models.UserProfileModelTest.test_user_profile_creation
```

### カバレッジ付きテスト実行

```bash
# カバレッジ付きでテスト実行
docker-compose exec agri_iot coverage run --source='.' manage.py test agri_app.tests

# カバレッジレポートを表示
docker-compose exec agri_iot coverage report

# HTMLレポートを生成
docker-compose exec agri_iot coverage html
```

### 詳細出力でのテスト実行

```bash
# 詳細出力（レベル2）でテスト実行
docker-compose exec agri_iot python manage.py test agri_app.tests -v 2

# デバッグSQLを表示
docker-compose exec agri_iot python manage.py test agri_app.tests --debug-sql
```

## テストデータの管理

### テストデータの読み込み

```bash
# テストデータを読み込んでテスト実行
docker-compose exec agri_iot python manage.py loaddata agri_app/model/yaml/testdata/01_initial.yaml
docker-compose exec agri_iot python manage.py test agri_app.tests
```

### テストデータベースのリセット

```bash
# テストデータベースをリセット
docker-compose exec agri_iot python manage.py flush --noinput
```

## トラブルシューティング

### よくある問題と解決方法

#### 1. テストが失敗する場合

```bash
# 詳細なエラー情報を確認
docker-compose exec agri_iot python manage.py test agri_app.tests -v 2

# ログを確認
docker-compose logs agri_iot
```

#### 2. データベース接続エラー

```bash
# データベースの状態を確認
docker-compose ps

# データベースを再起動
docker-compose restart db
```

#### 3. インポートエラー

```bash
# 依存関係を再インストール
docker-compose exec agri_iot pip install -r requirements.txt
```

#### 4. メモリ不足エラー

```bash
# テストを分割して実行
./agri_iot/run_tests.sh --models
./agri_iot/run_tests.sh --views
./agri_iot/run_tests.sh --forms
```

### デバッグ方法

#### 1. 特定のテストをデバッグ

```bash
# 特定のテストのみ実行
docker-compose exec agri_iot python manage.py test agri_app.tests.test_models.UserProfileModelTest.test_user_profile_creation -v 2
```

#### 2. テスト環境でのシェル実行

```bash
# テスト環境でシェルを起動
docker-compose exec agri_iot python manage.py shell
```

#### 3. テスト設定の確認

```bash
# テスト設定を確認
docker-compose exec agri_iot python manage.py check --deploy
```

## パフォーマンス最適化

### 1. 並列テスト実行

```bash
# 複数のテストファイルを並列実行
docker-compose exec agri_iot python manage.py test agri_app.tests.test_models agri_app.tests.test_views --parallel
```

### 2. テストの高速化

```bash
# データベースをメモリ内で実行
docker-compose exec agri_iot python manage.py test agri_app.tests --keepdb
```

### 3. カバレッジの最適化

```bash
# 特定のディレクトリのみカバレッジを測定
docker-compose exec agri_iot coverage run --source='agri_app' manage.py test agri_app.tests
```

## CI/CDでの使用

### GitHub Actionsでの使用例

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          docker-compose up -d
          ./agri_iot/run_tests.sh --all --coverage
```

### ローカルCI/CD

```bash
# テストを実行して結果を保存
./agri_iot/run_tests.sh --all --coverage > test_results.log 2>&1

# 結果を確認
cat test_results.log
```

## ベストプラクティス

### 1. テストの実行順序

1. 単体テスト（models, utils）
2. 統合テスト（forms, views）
3. エンドツーエンドテスト（integration）

### 2. テストの実行頻度

- 開発中：変更した部分のテストのみ実行
- コミット前：関連するテストカテゴリを実行
- プルリクエスト前：全てのテストを実行

### 3. カバレッジの管理

- 最低80%のカバレッジを維持
- 新機能追加時は対応するテストも追加
- 定期的にカバレッジレポートを確認

## 参考資料

- [Django テストドキュメント](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Coverage.py ドキュメント](https://coverage.readthedocs.io/)
- [Docker Compose ドキュメント](https://docs.docker.com/compose/) 