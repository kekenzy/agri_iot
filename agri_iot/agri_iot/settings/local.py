from .base import *

# DEBUG = False
DEBUG = True


# 以下有効にすると、500エラーなる
ALLOWED_HOSTS = ['*']
# ALLOWED_HOSTS += ['127.0.0.1', 'localhost']

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


# 追加
if DEBUG:
  INTERNAL_IPS = ['127.0.0.1', 'localhost']

  DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK" : lambda request: True,
    'IS_RUNNING_TESTS': True,
  }

# 開発環境用メール設定（Gmail SMTP）
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'your-email@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'your-app-password')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'your-email@gmail.com')

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

# 開発環境用データベース設定（PostgreSQL）
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'agri_db',
        'USER': 'agri_user',
        'PASSWORD': 'agri_user',
        'HOST': 'db',
        'PORT': '5432',
    }
}
