"""
テスト設定とテストランナーの設定
"""

import os
import sys
from django.conf import settings
from django.test.utils import get_runner

# テスト用の設定
TEST_SETTINGS = {
    'DATABASES': {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',  # メモリ内データベースを使用
        }
    },
    'INSTALLED_APPS': [
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'agri_app',
    ],
    'MIDDLEWARE': [
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ],
    'ROOT_URLCONF': 'agri_iot.urls',
    'TEMPLATES': [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [os.path.join(os.path.dirname(__file__), '..', '..', 'templates')],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ],
    'WSGI_APPLICATION': 'agri_iot.wsgi.application',
    'SECRET_KEY': 'test-secret-key-for-testing-only',
    'DEBUG': True,
    'ALLOWED_HOSTS': ['*'],
    'STATIC_URL': '/static/',
    'MEDIA_URL': '/media/',
    'STATIC_ROOT': os.path.join(os.path.dirname(__file__), '..', '..', 'staticfiles'),
    'MEDIA_ROOT': os.path.join(os.path.dirname(__file__), '..', '..', 'media'),
    'LANGUAGE_CODE': 'ja',
    'TIME_ZONE': 'Asia/Tokyo',
    'USE_I18N': True,
    'USE_TZ': True,
    'DEFAULT_AUTO_FIELD': 'django.db.models.BigAutoField',
    'MESSAGE_STORAGE': 'django.contrib.messages.storage.session.SessionStorage',
    'SESSION_ENGINE': 'django.contrib.sessions.backends.db',
    'LOGIN_URL': '/login/',
    'LOGIN_REDIRECT_URL': '/',
    'LOGOUT_REDIRECT_URL': '/login/',
    # テスト用のAWS S3設定（モック用）
    'AWS_ACCESS_KEY_ID': 'test-access-key',
    'AWS_SECRET_ACCESS_KEY': 'test-secret-key',
    'AWS_STORAGE_BUCKET_NAME': 'test-bucket',
    'AWS_S3_REGION_NAME': 'us-east-1',
    'AWS_DEFAULT_ACL': None,
    'AWS_S3_OBJECT_PARAMETERS': {
        'CacheControl': 'max-age=86400',
    },
    # テスト用のメール設定
    'EMAIL_BACKEND': 'django.core.mail.backends.locmem.EmailBackend',
    'DEFAULT_FROM_EMAIL': 'test@example.com',
    # テスト用のログ設定
    'LOGGING': {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
            'file': {
                'class': 'logging.FileHandler',
                'filename': '/tmp/test.log',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': False,
            },
            'agri_app': {
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
                'propagate': False,
            },
        },
    },
}


def run_tests():
    """
    テストを実行する関数
    """
    # テスト設定を適用
    for key, value in TEST_SETTINGS.items():
        setattr(settings, key, value)
    
    # テストランナーを取得
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # テストを実行
    failures = test_runner.run_tests(['agri_app.tests'])
    
    if failures:
        sys.exit(1)


def run_specific_tests(test_labels):
    """
    特定のテストを実行する関数
    
    Args:
        test_labels (list): 実行するテストのラベルリスト
    """
    # テスト設定を適用
    for key, value in TEST_SETTINGS.items():
        setattr(settings, key, value)
    
    # テストランナーを取得
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # 特定のテストを実行
    failures = test_runner.run_tests(test_labels)
    
    if failures:
        sys.exit(1)


def run_model_tests():
    """モデルテストのみを実行"""
    run_specific_tests(['agri_app.tests.test_models'])


def run_view_tests():
    """ビューテストのみを実行"""
    run_specific_tests(['agri_app.tests.test_views'])


def run_form_tests():
    """フォームテストのみを実行"""
    run_specific_tests(['agri_app.tests.test_forms'])


def run_util_tests():
    """ユーティリティテストのみを実行"""
    run_specific_tests(['agri_app.tests.test_utils'])


def run_integration_tests():
    """統合テストのみを実行"""
    run_specific_tests(['agri_app.tests.test_integration'])


# テストカバレッジ設定
COVERAGE_SETTINGS = {
    'COVERAGE_MODULE_EXCLUDES': [
        'tests$',
        'settings$',
        'urls$',
        'wsgi$',
        'manage$',
        'migrations$',
        '__init__$',
    ],
    'COVERAGE_REPORT_HTML_OUTPUT_DIR': 'htmlcov',
    'COVERAGE_REPORT_TERMINAL_OUTPUT': True,
    'COVERAGE_USE_STDOUT': True,
    'COVERAGE_FAIL_UNDER': 80,  # 80%以上のカバレッジを要求
}


# テストパフォーマンス設定
PERFORMANCE_SETTINGS = {
    'TEST_TIMEOUT': 30,  # テストタイムアウト（秒）
    'SLOW_TEST_THRESHOLD': 1.0,  # 遅いテストの閾値（秒）
    'MAX_MEMORY_USAGE': 512,  # 最大メモリ使用量（MB）
}


# テストデータ設定
TEST_DATA_SETTINGS = {
    'FIXTURE_DIRS': [
        os.path.join(os.path.dirname(__file__), '..', 'model', 'yaml', 'testdata'),
    ],
    'TEST_DATA_FILES': [
        '01_initial.yaml',
        'cp_home_01_test_data.yaml',
        'inquiry_test.yaml',
        'mail_test.yaml',
        'service_group_detail_test_data.yaml',
    ],
}


# テスト環境変数
TEST_ENV_VARS = {
    'DJANGO_SETTINGS_MODULE': 'agri_iot.settings.local',
    'PYTHONPATH': os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'TESTING': 'True',
    'DEBUG': 'True',
}


def setup_test_environment():
    """
    テスト環境をセットアップする関数
    """
    # 環境変数を設定
    for key, value in TEST_ENV_VARS.items():
        os.environ[key] = value
    
    # テスト用ディレクトリを作成
    test_dirs = [
        TEST_SETTINGS['STATIC_ROOT'],
        TEST_SETTINGS['MEDIA_ROOT'],
        COVERAGE_SETTINGS['COVERAGE_REPORT_HTML_OUTPUT_DIR'],
    ]
    
    for directory in test_dirs:
        os.makedirs(directory, exist_ok=True)


def cleanup_test_environment():
    """
    テスト環境をクリーンアップする関数
    """
    import shutil
    
    # テスト用ディレクトリを削除
    test_dirs = [
        TEST_SETTINGS['STATIC_ROOT'],
        TEST_SETTINGS['MEDIA_ROOT'],
        COVERAGE_SETTINGS['COVERAGE_REPORT_HTML_OUTPUT_DIR'],
    ]
    
    for directory in test_dirs:
        if os.path.exists(directory):
            shutil.rmtree(directory)


if __name__ == '__main__':
    # 直接実行された場合の処理
    import argparse
    
    parser = argparse.ArgumentParser(description='テストを実行します')
    parser.add_argument('--models', action='store_true', help='モデルテストのみ実行')
    parser.add_argument('--views', action='store_true', help='ビューテストのみ実行')
    parser.add_argument('--forms', action='store_true', help='フォームテストのみ実行')
    parser.add_argument('--utils', action='store_true', help='ユーティリティテストのみ実行')
    parser.add_argument('--integration', action='store_true', help='統合テストのみ実行')
    parser.add_argument('--setup', action='store_true', help='テスト環境をセットアップ')
    parser.add_argument('--cleanup', action='store_true', help='テスト環境をクリーンアップ')
    
    args = parser.parse_args()
    
    if args.setup:
        setup_test_environment()
        print("テスト環境のセットアップが完了しました")
    elif args.cleanup:
        cleanup_test_environment()
        print("テスト環境のクリーンアップが完了しました")
    elif args.models:
        run_model_tests()
    elif args.views:
        run_view_tests()
    elif args.forms:
        run_form_tests()
    elif args.utils:
        run_util_tests()
    elif args.integration:
        run_integration_tests()
    else:
        run_tests() 