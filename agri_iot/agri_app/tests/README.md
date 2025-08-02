# Agri IoT テストスイート

このディレクトリには、Agri IoTアプリケーションの包括的なテストスイートが含まれています。

## テスト構成

### テストファイル

- `test_models.py` - モデルのテスト
- `test_views.py` - ビューのテスト
- `test_forms.py` - フォームのテスト
- `test_utils.py` - ユーティリティ関数のテスト
- `test_integration.py` - 統合テスト
- `test_settings.py` - テスト設定とランナー

### テストカテゴリ

#### 1. モデルテスト (`test_models.py`)
- `UserProfileModelTest` - ユーザープロフィールモデルのテスト
- `GroupProfileModelTest` - グループプロフィールモデルのテスト
- `BaseMetaModelTest` - 基底メタクラスのテスト
- `ModelIntegrationTest` - モデル統合テスト

#### 2. ビューテスト (`test_views.py`)
- `AuthenticationViewsTest` - 認証ビューのテスト
- `UserManagementViewsTest` - ユーザー管理ビューのテスト
- `GroupManagementViewsTest` - グループ管理ビューのテスト
- `ProfileViewsTest` - プロフィールビューのテスト
- `PasswordResetViewsTest` - パスワードリセットビューのテスト
- `S3FileManagementViewsTest` - S3ファイル管理ビューのテスト
- `ErrorHandlingViewsTest` - エラーハンドリングビューのテスト
- `PermissionTests` - 権限テスト
- `IntegrationTests` - 統合テスト

#### 3. フォームテスト (`test_forms.py`)
- `LoginFormTest` - ログインフォームのテスト
- `UserSearchFormTest` - ユーザー検索フォームのテスト
- `UserFormTest` - ユーザーフォームのテスト
- `GroupSearchFormTest` - グループ検索フォームのテスト
- `GroupFormTest` - グループフォームのテスト
- `GroupProfileFormTest` - グループプロフィールフォームのテスト
- `GroupMemberFormTest` - グループメンバーフォームのテスト
- `ProfileEditFormTest` - プロフィール編集フォームのテスト
- `ProfilePasswordChangeFormTest` - パスワード変更フォームのテスト
- `UploadFileFormTest` - ファイルアップロードフォームのテスト
- `FormIntegrationTest` - フォーム統合テスト

#### 4. ユーティリティテスト (`test_utils.py`)
- `AWSS3UtilTest` - AWS S3ユーティリティのテスト
- `DateTimeUtilTest` - 日時ユーティリティのテスト
- `LoggingUtilTest` - ログユーティリティのテスト
- `RequestUtilTest` - リクエストユーティリティのテスト
- `ValidatorUtilTest` - バリデーターのテスト
- `IntegrationUtilTest` - ユーティリティ統合テスト

#### 5. 統合テスト (`test_integration.py`)
- `EndToEndWorkflowTest` - エンドツーエンドワークフローのテスト
- `DatabaseIntegrationTest` - データベース統合テスト
- `APIIntegrationTest` - API統合テスト
- `SecurityIntegrationTest` - セキュリティ統合テスト

## テストの実行方法

### 基本的なテスト実行

```bash
# 全てのテストを実行
python manage.py test agri_app.tests

# 特定のテストファイルを実行
python manage.py test agri_app.tests.test_models
python manage.py test agri_app.tests.test_views
python manage.py test agri_app.tests.test_forms
python manage.py test agri_app.tests.test_utils
python manage.py test agri_app.tests.test_integration

# 特定のテストクラスを実行
python manage.py test agri_app.tests.test_models.UserProfileModelTest

# 特定のテストメソッドを実行
python manage.py test agri_app.tests.test_models.UserProfileModelTest.test_user_profile_creation
```

### テスト設定を使用した実行

```bash
# テスト設定を使用してテストを実行
python agri_app/tests/test_settings.py

# 特定のテストカテゴリのみ実行
python agri_app/tests/test_settings.py --models
python agri_app/tests/test_settings.py --views
python agri_app/tests/test_settings.py --forms
python agri_app/tests/test_settings.py --utils
python agri_app/tests/test_settings.py --integration

# テスト環境のセットアップ/クリーンアップ
python agri_app/tests/test_settings.py --setup
python agri_app/tests/test_settings.py --cleanup
```

### カバレッジ付きテスト実行

```bash
# coverageをインストール
pip install coverage

# カバレッジ付きでテスト実行
coverage run --source='.' manage.py test agri_app.tests

# カバレッジレポートを表示
coverage report

# HTMLレポートを生成
coverage html
```

### パフォーマンステスト

```bash
# パフォーマンステストを実行
python manage.py test agri_app.tests.test_integration.PerformanceIntegrationTest
```

## テストデータ

### テストデータファイル

テストデータは以下のYAMLファイルで管理されています：

- `agri_app/model/yaml/testdata/01_initial.yaml`
- `agri_app/model/yaml/testdata/cp_home_01_test_data.yaml`
- `agri_app/model/yaml/testdata/inquiry_test.yaml`
- `agri_app/model/yaml/testdata/mail_test.yaml`
- `agri_app/model/yaml/testdata/service_group_detail_test_data.yaml`

### テストデータの読み込み

```bash
# テストデータを読み込んでテスト実行
python manage.py loaddata agri_app/model/yaml/testdata/01_initial.yaml
python manage.py test agri_app.tests
```

## テスト設定

### テスト用データベース

テストでは、メモリ内SQLiteデータベースを使用して高速なテスト実行を実現しています。

### モック設定

外部サービス（AWS S3、メール送信など）はモックを使用してテストしています。

### 環境変数

テスト実行時は以下の環境変数が設定されます：

- `DJANGO_SETTINGS_MODULE=agri_iot.settings.local`
- `TESTING=True`
- `DEBUG=True`

## テストの書き方

### 新しいテストを追加する場合

1. 適切なテストファイルを選択または新規作成
2. `TestCase`を継承したクラスを作成
3. `setUp`メソッドでテストデータを準備
4. テストメソッドを`test_`で始まる名前で作成
5. アサーションを使用して期待値を検証

### テストの例

```python
from django.test import TestCase
from django.contrib.auth.models import User
from agri_app.models import UserProfile

class MyModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(user=self.user)

    def test_profile_creation(self):
        """プロフィールが正しく作成されることをテスト"""
        self.assertEqual(self.profile.user, self.user)
        self.assertIsNotNone(self.profile.create_at)
```

## テストのベストプラクティス

### 1. テストの独立性
- 各テストは独立して実行できるようにする
- テスト間でデータを共有しない
- `setUp`と`tearDown`を適切に使用

### 2. テストの可読性
- テストメソッド名は説明的にする
- ドキュメント文字列でテストの目的を説明
- アサーションメッセージを明確にする

### 3. テストの保守性
- テストデータは`setUp`で作成
- 共通のテストデータは`TestCase`クラスで管理
- テストヘルパーメソッドを作成して再利用

### 4. パフォーマンス
- データベースクエリを最小限に抑える
- 必要に応じて`select_related`や`prefetch_related`を使用
- 大量データのテストは適切にモック化

## トラブルシューティング

### よくある問題

1. **インポートエラー**
   - `PYTHONPATH`が正しく設定されているか確認
   - 必要なパッケージがインストールされているか確認

2. **データベースエラー**
   - マイグレーションが最新か確認
   - テストデータベースが正しく作成されているか確認

3. **モックエラー**
   - 外部サービスのモックが正しく設定されているか確認
   - テスト設定でモックが有効になっているか確認

### デバッグ方法

```bash
# 詳細な出力でテスト実行
python manage.py test agri_app.tests -v 2

# 特定のテストをデバッグモードで実行
python manage.py test agri_app.tests.test_models -v 2 --debug-mode

# テストの実行時間を表示
python manage.py test agri_app.tests --debug-sql
```

## 継続的インテグレーション

### CI/CD設定

テストは以下のCI/CDパイプラインで自動実行されます：

1. プルリクエスト作成時
2. マージ前の自動テスト
3. デプロイ前の統合テスト

### テスト結果の報告

- テスト結果はCI/CDダッシュボードで確認可能
- カバレッジレポートは自動生成
- 失敗したテストは詳細なログと共に報告

## 貢献ガイドライン

### テストの追加

1. 新しい機能を追加する際は、対応するテストも追加
2. バグ修正時は、再発防止のためのテストを追加
3. テストカバレッジを80%以上に維持

### テストの改善

1. 既存のテストを定期的に見直し
2. パフォーマンスの改善
3. テストの可読性向上

### レビュープロセス

1. プルリクエストにはテストを含める
2. テストの品質をレビュー
3. カバレッジの確認

## ライセンス

このテストスイートは、Agri IoTプロジェクトの一部として提供されています。 