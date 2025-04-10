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
}


# 追加
if DEBUG:
  INTERNAL_IPS = ['127.0.0.1', 'localhost']

  DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK" : lambda request: True,
  }
