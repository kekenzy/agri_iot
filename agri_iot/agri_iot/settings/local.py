from .base import *

# DEBUG = False
DEBUG = True


# 以下有効にすると、500エラーなる
ALLOWED_HOSTS = ['*']
# ALLOWED_HOSTS += ['127.0.0.1', 'localhost']

# Debug Toolbar設定
import sys
if 'test' not in sys.argv:
    # テスト実行時以外はDebug Toolbarを有効化
    INSTALLED_APPS += [
        'debug_toolbar',
    ]

    # 以下有効にすると、500エラーなる
    MIDDLEWARE += [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]

    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda x: True,
        'SHOW_TEMPLATE_CONTEXT': True,
        'IS_RUNNING_TESTS': True,
    }
else:
    # テスト実行時はDebug Toolbarを完全に無効化
    DEBUG_TOOLBAR_CONFIG = {
        'IS_RUNNING_TESTS': True,
    }

# 追加
if DEBUG and 'test' not in sys.argv:
  INTERNAL_IPS = ['127.0.0.1', 'localhost']

# 開発環境用メール設定（MailHog）
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mailhog'  # Dockerサービス名
EMAIL_PORT = 1025       # MailHogのSMTPポート
EMAIL_USE_TLS = False   # MailHogはTLSを使用しない
EMAIL_HOST_USER = ''    # MailHogは認証不要
EMAIL_HOST_PASSWORD = '' # MailHogは認証不要
DEFAULT_FROM_EMAIL = 'noreply@example.com'

# 開発環境用静的ファイル設定
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
STATIC_URL = '/static/'

# キャッシュ無効化
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# 開発環境用ミドルウェア（キャッシュ無効化）
MIDDLEWARE += [
    'django.middleware.cache.UpdateCacheMiddleware',
]

# キャッシュ設定（開発環境では無効）
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Docker環境用データベース設定（PostgreSQL）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'agri_db',
        'USER': 'agri_user',
        'PASSWORD': 'agri_user',
        'HOST': 'db',  # Docker環境ではサービス名を使用
        'PORT': '5432',
    }
}
