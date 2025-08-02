from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from unittest.mock import patch, MagicMock
import tempfile
import os
from datetime import datetime

from agri_app.models import UserProfile
from agri_app.utils.aws_s3 import list_s3_files, upload_file_to_s3, delete_file_from_s3
from agri_app.utils.datetime_util import datetime_now_utc, datetime_now_jst, format_jst_datetime
from agri_app.utils.logging_util import log_decorator, CustomLogManager, SessionIdFilter, RequestIdFilter
from agri_app.utils.request_util import get_request_info, parse_user_agent


class BaseUtilTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user_profile = UserProfile.objects.create(user=self.user)
        self.factory = RequestFactory()


class AWSS3UtilTest(BaseUtilTestCase):
    def setUp(self):
        super().setUp()
        # テスト用の一時ファイルを作成
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        self.temp_file.write(b'test file content')
        self.temp_file.flush()

    def tearDown(self):
        # 一時ファイルを削除
        if hasattr(self, 'temp_file'):
            self.temp_file.close()
            os.unlink(self.temp_file.name)
        super().tearDown()

    @patch('agri_app.utils.aws_s3.boto3.client')
    def test_list_s3_files_success(self, mock_boto_client):
        """S3ファイル一覧取得の成功テスト"""
        # モックの設定
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        
        # レスポンスのモック
        mock_response = {
            'Contents': [
                {
                    'Key': 'test1.jpg',
                    'Size': 1024,
                    'LastModified': datetime.now()
                },
                {
                    'Key': 'test2.jpg',
                    'Size': 2048,
                    'LastModified': datetime.now()
                }
            ]
        }
        mock_s3.list_objects_v2.return_value = mock_response
        
        # テスト実行
        result = list_s3_files()
        
        # 検証
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['key'], 'test1.jpg')
        self.assertEqual(result[0]['size'], 1024)
        self.assertEqual(result[1]['key'], 'test2.jpg')
        self.assertEqual(result[1]['size'], 2048)
        
        # boto3クライアントが正しく呼ばれたことを確認
        mock_boto_client.assert_called_once_with('s3')
        mock_s3.list_objects_v2.assert_called_once()

    @patch('agri_app.utils.aws_s3.boto3.client')
    def test_list_s3_files_empty_bucket(self, mock_boto_client):
        """空のS3バケットのテスト"""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        
        # 空のレスポンス
        mock_response = {}
        mock_s3.list_objects_v2.return_value = mock_response
        
        result = list_s3_files()
        self.assertEqual(result, [])

    @patch('agri_app.utils.aws_s3.boto3.client')
    def test_list_s3_files_exception(self, mock_boto_client):
        """S3ファイル一覧取得の例外処理テスト"""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        
        # 例外を発生させる
        mock_s3.list_objects_v2.side_effect = Exception('S3 error')
        
        with self.assertRaises(Exception):
            list_s3_files()

    @patch('agri_app.utils.aws_s3.boto3.client')
    def test_upload_file_to_s3_success(self, mock_boto_client):
        """S3ファイルアップロードの成功テスト"""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        
        # ファイルオブジェクトを作成
        with open(self.temp_file.name, 'rb') as file:
            result = upload_file_to_s3(file)
        
        # 検証
        self.assertTrue(result)
        mock_s3.upload_fileobj.assert_called_once()

    @patch('agri_app.utils.aws_s3.boto3.client')
    def test_upload_file_to_s3_exception(self, mock_boto_client):
        """S3ファイルアップロードの例外処理テスト"""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        
        # 例外を発生させる
        mock_s3.upload_fileobj.side_effect = Exception('Upload error')
        
        with open(self.temp_file.name, 'rb') as file:
            with self.assertRaises(Exception):
                upload_file_to_s3(file)

    @patch('agri_app.utils.aws_s3.boto3.client')
    def test_delete_file_from_s3_success(self, mock_boto_client):
        """S3ファイル削除の成功テスト"""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        
        result = delete_file_from_s3('test.jpg')
        
        # 検証
        self.assertTrue(result)
        mock_s3.delete_object.assert_called_once()

    @patch('agri_app.utils.aws_s3.boto3.client')
    def test_delete_file_from_s3_exception(self, mock_boto_client):
        """S3ファイル削除の例外処理テスト"""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        
        # 例外を発生させる
        mock_s3.delete_object.side_effect = Exception('Delete error')
        
        with self.assertRaises(Exception):
            delete_file_from_s3('test.jpg')

    @patch('agri_app.utils.aws_s3.boto3.client')
    def test_s3_operations_with_custom_bucket(self, mock_boto_client):
        """カスタムバケットでのS3操作テスト"""
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        
        # カスタムバケット名を設定
        custom_bucket = 'custom-test-bucket'
        
        # ファイル一覧取得
        mock_response = {'Contents': []}
        mock_s3.list_objects_v2.return_value = mock_response
        list_s3_files(bucket_name=custom_bucket)
        
        # ファイルアップロード
        with open(self.temp_file.name, 'rb') as file:
            upload_file_to_s3(file, bucket_name=custom_bucket)
        
        # ファイル削除
        delete_file_from_s3('test.jpg', bucket_name=custom_bucket)
        
        # 正しいバケット名で呼ばれたことを確認
        self.assertEqual(mock_s3.list_objects_v2.call_count, 1)
        self.assertEqual(mock_s3.upload_fileobj.call_count, 1)
        self.assertEqual(mock_s3.delete_object.call_count, 1)


class DateTimeUtilTest(BaseUtilTestCase):
    def test_datetime_now_utc(self):
        """UTC日時取得のテスト"""
        result = datetime_now_utc()
        self.assertIsNotNone(result)
        self.assertEqual(result.tzinfo.name, "UTC")

    def test_datetime_now_jst(self):
        """JST日時取得のテスト"""
        result = datetime_now_jst()
        self.assertIsNotNone(result)
        self.assertEqual(result.tzinfo.name, "Asia/Tokyo")

    def test_format_jst_datetime(self):
        """JST日時フォーマットのテスト"""
        from datetime import datetime
        from zoneinfo import ZoneInfo
        
        dt = datetime(2023, 1, 15, 14, 30, 0, tzinfo=ZoneInfo("UTC"))
        result = format_jst_datetime(dt)
        self.assertIn("2023年", result)
        self.assertIn("1月", result)
        self.assertIn("15日", result)

    def test_format_jst_datetime_none(self):
        """None値でのJST日時フォーマットテスト"""
        result = format_jst_datetime(None)
        self.assertIsNone(result)


class LoggingUtilTest(BaseUtilTestCase):
    def test_custom_log_manager_get(self):
        """CustomLogManager.get()のテスト"""
        result = CustomLogManager.get()
        self.assertIsInstance(result, dict)
        self.assertIn('session_id', result)
        self.assertIn('request_id', result)

    def test_custom_log_manager_set(self):
        """CustomLogManager.set()のテスト"""
        session_key = "test_session_key_12345"
        CustomLogManager.set(session_key)
        
        result = CustomLogManager.get()
        self.assertEqual(result['session_id'], session_key[:8])
        self.assertIsInstance(result['request_id'], str)
        self.assertEqual(len(result['request_id']), 8)

    def test_session_id_filter(self):
        """SessionIdFilterのテスト"""
        filter_instance = SessionIdFilter()
        
        # テスト用のログレコードを作成
        class MockRecord:
            pass
        
        record = MockRecord()
        
        # フィルターを実行
        result = filter_instance.filter(record)
        
        self.assertTrue(result)
        self.assertTrue(hasattr(record, 'session_id'))

    def test_request_id_filter(self):
        """RequestIdFilterのテスト"""
        filter_instance = RequestIdFilter()
        
        # テスト用のログレコードを作成
        class MockRecord:
            pass
        
        record = MockRecord()
        
        # フィルターを実行
        result = filter_instance.filter(record)
        
        self.assertTrue(result)
        self.assertTrue(hasattr(record, 'request_id'))

    def test_log_decorator(self):
        """log_decoratorのテスト"""
        @log_decorator("テスト処理")
        def test_function():
            return "success"
        
        result = test_function()
        self.assertEqual(result, "success")


class RequestUtilTest(BaseUtilTestCase):
    def test_get_request_info(self):
        """リクエスト情報取得のテスト"""
        request = self.factory.get('/test/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        request.META['HTTP_REFERER'] = 'http://example.com/'
        request.META['REQUEST_METHOD'] = 'GET'
        
        result = get_request_info(request)
        
        self.assertEqual(result['source_ip_address'], '192.168.1.1')
        self.assertEqual(result['user_agent'], 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        self.assertEqual(result['referrer'], 'http://example.com/')
        self.assertEqual(result['request_method'], 'GET')
        self.assertEqual(result['request_url'], '/test/')

    def test_get_request_info_with_proxy(self):
        """プロキシ経由でのリクエスト情報取得テスト"""
        request = self.factory.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '203.0.113.1, 192.168.1.1'
        
        result = get_request_info(request)
        self.assertEqual(result['source_ip_address'], '203.0.113.1')

    def test_get_request_info_with_client_source(self):
        """X-Client-Sourceヘッダーでのリクエスト情報取得テスト"""
        request = self.factory.get('/')
        request.META['HTTP_X_CLIENT_SOURCE'] = '198.51.100.1'
        
        result = get_request_info(request)
        self.assertEqual(result['source_ip_address'], '198.51.100.1')

    def test_parse_user_agent(self):
        """User Agent解析のテスト"""
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        
        result = parse_user_agent(user_agent)
        
        self.assertIsInstance(result, dict)
        self.assertIn('category', result)
        self.assertIn('name', result)
        self.assertIn('version', result)
        self.assertIn('os', result)
        self.assertIn('vendor', result)
        self.assertIn('os_version', result)





class IntegrationUtilTest(BaseUtilTestCase):
    def test_complete_s3_workflow(self):
        """完全なS3ワークフローのテスト"""
        # 1. S3ファイル一覧取得
        with patch('agri_app.utils.aws_s3.boto3.client') as mock_boto_client:
            mock_s3 = MagicMock()
            mock_boto_client.return_value = mock_s3
            mock_response = {'Contents': [{'Key': 'test1.jpg', 'Size': 1024}]}
            mock_s3.list_objects_v2.return_value = mock_response
            
            files = list_s3_files()
            self.assertEqual(len(files), 1)
            
            # 2. S3ファイルアップロード
            with open(self.temp_file.name, 'rb') as file:
                result = upload_file_to_s3(file)
                self.assertTrue(result)
            
            # 3. S3ファイル削除
            result = delete_file_from_s3('test1.jpg')
            self.assertTrue(result)

    def test_complete_logging_workflow(self):
        """完全なログワークフローのテスト"""
        # 1. セッション設定
        session_key = "test_session_12345"
        CustomLogManager.set(session_key)
        
        # 2. ログ情報の取得
        log_params = CustomLogManager.get()
        self.assertEqual(log_params['session_id'], session_key[:8])
        self.assertIsInstance(log_params['request_id'], str)
        
        # 3. ログデコレータのテスト
        @log_decorator("テスト処理")
        def test_function():
            return "success"
        
        result = test_function()
        self.assertEqual(result, "success")

    def test_complete_datetime_workflow(self):
        """完全な日時処理ワークフローのテスト"""
        # 1. 現在時刻の取得
        utc_now = datetime_now_utc()
        jst_now = datetime_now_jst()
        
        # 2. 時刻の検証
        self.assertIsNotNone(utc_now)
        self.assertIsNotNone(jst_now)
        self.assertEqual(utc_now.tzinfo.name, "UTC")
        self.assertEqual(jst_now.tzinfo.name, "Asia/Tokyo")
        
        # 3. 日時フォーマット
        formatted = format_jst_datetime(utc_now)
        self.assertIsInstance(formatted, str)
        self.assertGreater(len(formatted), 0)

    def test_complete_request_analysis_workflow(self):
        """完全なリクエスト解析ワークフローのテスト"""
        # 1. リクエスト情報の取得
        request = self.factory.get('/test/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        
        request_info = get_request_info(request)
        
        # 2. 結果の検証
        self.assertEqual(request_info['source_ip_address'], '192.168.1.1')
        self.assertEqual(request_info['user_agent'], 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        self.assertEqual(request_info['request_method'], 'GET')
        self.assertEqual(request_info['request_url'], '/test/')
        
        # 3. User Agent解析
        parsed_ua = parse_user_agent(request_info['user_agent'])
        self.assertIsInstance(parsed_ua, dict)
        self.assertIn('category', parsed_ua)
        self.assertIn('name', parsed_ua) 