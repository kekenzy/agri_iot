# スタイル設定機能

## 概要

この機能により、管理画面でスタイルシートを切り替えて、アプリケーションの見た目を動的に変更できます。

## 機能

### 1. 利用可能なスタイル

- **ベーススタイル**: シンプルで使いやすいデザイン
- **KUUMAスタイル**: ミニマルで洗練されたデザイン
- **ダークテーマ**: 目に優しいダークデザイン
- **カラフルテーマ**: 鮮やかで楽しいデザイン

### 2. 管理機能

#### 管理画面での設定
- スタイル設定の作成・編集・削除
- デフォルトスタイルの設定
- 設定の詳細管理

#### ユーザーインターフェース
- スタイル設定管理ページ（`/style_settings`）
- 現在のスタイル表示
- スタイル切り替え機能

## 使用方法

### 1. 管理画面での設定

1. 管理画面にログイン（`/admin`）
2. 「スタイル設定」セクションに移動
3. 新しいスタイル設定を作成または既存の設定を編集
4. デフォルト設定として設定したいスタイルを選択

### 2. ユーザーインターフェースでの設定

1. アプリケーションにログイン
2. プロフィールメニューから「スタイル設定」を選択
3. 利用可能なスタイル設定を確認
4. 「デフォルトに設定」ボタンでスタイルを切り替え

## ファイル構成

```
agri_iot/
├── static/css/
│   ├── base-style.css      # ベーススタイル
│   ├── kuuma-style.css     # KUUMAスタイル
│   ├── dark-style.css      # ダークテーマ
│   └── colorful-style.css  # カラフルテーマ
├── templates/
│   └── style_settings/
│       └── style_settings.html  # スタイル設定管理ページ
├── agri_app/
│   ├── models.py           # StyleSettingsモデル
│   ├── views.py            # スタイル設定ビュー
│   ├── admin.py            # 管理画面設定
│   ├── urls.py             # URL設定
│   └── templatetags/
│       └── style_tags.py   # カスタムテンプレートタグ
```

## 技術仕様

### モデル

```python
class StyleSettings(BaseMeta):
    STYLE_CHOICES = [
        ('base', 'ベーススタイル'),
        ('kuuma', 'KUUMAスタイル'),
        ('dark', 'ダークテーマ'),
        ('colorful', 'カラフルテーマ'),
    ]
    
    name = models.CharField(max_length=50, verbose_name='設定名', unique=True)
    active_style = models.CharField(max_length=20, choices=STYLE_CHOICES, default='base')
    is_default = models.BooleanField(default=False, verbose_name='デフォルト設定')
    description = models.TextField(blank=True, null=True, verbose_name='説明')
```

### テンプレートタグ

```python
@register.simple_tag
def get_active_style():
    """現在アクティブなスタイルを取得するテンプレートタグ"""
    return StyleSettings.get_active_style()
```

### URL設定

```python
path("style_settings", views.style_settings, name="style_settings"),
```

## Docker環境での実行

### 1. コンテナの起動

```bash
docker-compose up -d
```

### 2. マイグレーションの実行

```bash
docker-compose exec agri_iot python manage.py migrate
```

### 3. 初期データの作成

```bash
docker-compose exec agri_iot python manage.py shell -c "
from agri_app.models import StyleSettings
StyleSettings.objects.get_or_create(name='デフォルト設定', defaults={'active_style': 'base', 'is_default': True, 'description': 'デフォルトのベーススタイル'})
StyleSettings.objects.get_or_create(name='KUUMAスタイル', defaults={'active_style': 'kuuma', 'is_default': False, 'description': 'ミニマルで洗練されたKUUMAスタイル'})
StyleSettings.objects.get_or_create(name='ダークテーマ', defaults={'active_style': 'dark', 'is_default': False, 'description': '目に優しいダークテーマ'})
StyleSettings.objects.get_or_create(name='カラフルテーマ', defaults={'active_style': 'colorful', 'is_default': False, 'description': '鮮やかで楽しいカラフルテーマ'})
print('Style settings created')
"
```

### 4. アクセス

- アプリケーション: http://localhost:8000
- 管理画面: http://localhost:8000/admin
- スタイル設定: http://localhost:8000/style_settings

## 注意事項

1. スタイル設定を変更した後、ページを再読み込みすると新しいスタイルが適用されます
2. デフォルト設定は同時に1つしか設定できません
3. 管理者またはスーパーユーザーのみがスタイル設定を変更できます

## カスタマイズ

新しいスタイルを追加する場合：

1. `static/css/` に新しいCSSファイルを作成
2. `models.py` の `STYLE_CHOICES` に新しいスタイルを追加
3. `base.html` のスタイル読み込み部分を更新
4. マイグレーションを作成・実行

## トラブルシューティング

### スタイルが適用されない場合

1. ブラウザのキャッシュをクリア
2. ページを強制リロード（Ctrl+F5）
3. スタイル設定が正しく保存されているか確認

### 管理画面にアクセスできない場合

1. スーパーユーザーアカウントが作成されているか確認
2. データベース接続が正常か確認
3. マイグレーションが実行されているか確認 