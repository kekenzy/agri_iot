from django.test import TestCase, Client
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages
from unittest.mock import patch, MagicMock
import tempfile
import os

from agri_app.models import UserProfile, GroupProfile


class BaseTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User',
            is_staff=True,
            is_superuser=True
        )
        self.user_profile = UserProfile.objects.create(user=self.user)
        self.admin_profile = UserProfile.objects.create(user=self.admin_user)


class AuthenticationViewsTest(BaseTestCase):
    def test_home_view(self):
        """ホーム画面のテスト"""
        response = self.client.get(reverse('agri_app:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_user_login_get(self):
        """ログイン画面のGETリクエストテスト"""
        response = self.client.get(reverse('agri_app:user_login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/login.html')
        self.assertIn('login_form', response.context)

    def test_user_login_success(self):
        """ログイン成功のテスト"""
        response = self.client.post(reverse('agri_app:user_login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertRedirects(response, reverse('agri_app:home'))

    def test_user_login_failure(self):
        """ログイン失敗のテスト"""
        response = self.client.post(reverse('agri_app:user_login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/login.html')

    def test_user_logout(self):
        """ログアウトのテスト"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('agri_app:user_logout'))
        self.assertRedirects(response, reverse('agri_app:user_login'))


class UserManagementViewsTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username='admin', password='adminpass123')

    def test_user_list_view(self):
        """ユーザー一覧画面のテスト"""
        response = self.client.get(reverse('agri_app:user_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_management/user_list.html')
        self.assertIn('users', response.context)
        self.assertIn('search_form', response.context)

    def test_user_list_search(self):
        """ユーザー一覧の検索機能テスト"""
        response = self.client.get(reverse('agri_app:user_list'), {
            'username': 'test',
            'first_name': 'Test'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('users', response.context)

    def test_user_detail_view(self):
        """ユーザー詳細画面のテスト"""
        response = self.client.get(reverse('agri_app:user_detail', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_management/user_detail.html')
        self.assertEqual(response.context['user_detail'], self.user)

    def test_user_edit_view_get(self):
        """ユーザー編集画面のGETリクエストテスト"""
        response = self.client.get(reverse('agri_app:user_edit', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_management/user_form.html')
        self.assertIn('form', response.context)

    def test_user_edit_view_post(self):
        """ユーザー編集のPOSTリクエストテスト"""
        response = self.client.post(reverse('agri_app:user_edit', args=[self.user.id]), {
            'username': 'updateduser',
            'first_name': 'Updated',
            'last_name': 'User',
            'email': 'updated@example.com'
        })
        self.assertRedirects(response, reverse('agri_app:user_detail', args=[self.user.id]))
        
        # ユーザーが更新されたことを確認
        updated_user = User.objects.get(id=self.user.id)
        self.assertEqual(updated_user.username, 'updateduser')

    def test_user_delete_view_get(self):
        """ユーザー削除確認画面のテスト"""
        response = self.client.get(reverse('agri_app:user_delete', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_management/user_confirm_delete.html')

    def test_user_delete_view_post(self):
        """ユーザー削除のテスト"""
        response = self.client.post(reverse('agri_app:user_delete', args=[self.user.id]))
        self.assertRedirects(response, reverse('agri_app:user_list'))
        
        # ユーザーが削除されたことを確認
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=self.user.id)


class GroupManagementViewsTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username='admin', password='adminpass123')
        self.group = Group.objects.create(name='Test Group')
        self.group_profile = GroupProfile.objects.create(
            group=self.group,
            description='Test group description',
            is_active=True,
            color='#ff0000'
        )

    def test_group_list_view(self):
        """グループ一覧画面のテスト"""
        response = self.client.get(reverse('agri_app:group_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'group_management/group_list.html')
        self.assertIn('groups', response.context)
        self.assertIn('search_form', response.context)

    def test_group_list_search(self):
        """グループ一覧の検索機能テスト"""
        response = self.client.get(reverse('agri_app:group_list'), {
            'name': 'Test',
            'is_active': 'True'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('groups', response.context)

    def test_group_create_view_get(self):
        """グループ作成画面のGETリクエストテスト"""
        response = self.client.get(reverse('agri_app:group_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'group_management/group_form.html')
        self.assertIn('group_form', response.context)
        self.assertIn('profile_form', response.context)

    def test_group_create_view_post(self):
        """グループ作成のPOSTリクエストテスト"""
        response = self.client.post(reverse('agri_app:group_create'), {
            'name': 'New Group',
            'description': 'New group description',
            'is_active': True,
            'color': '#00ff00'
        })
        self.assertRedirects(response, reverse('agri_app:group_list'))
        
        # グループが作成されたことを確認
        new_group = Group.objects.get(name='New Group')
        self.assertIsNotNone(new_group.groupprofile)
        self.assertEqual(new_group.groupprofile.description, 'New group description')

    def test_group_detail_view(self):
        """グループ詳細画面のテスト"""
        response = self.client.get(reverse('agri_app:group_detail', args=[self.group.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'group_management/group_detail.html')
        self.assertEqual(response.context['group'], self.group)
        self.assertEqual(response.context['profile'], self.group_profile)

    def test_group_edit_view_get(self):
        """グループ編集画面のGETリクエストテスト"""
        response = self.client.get(reverse('agri_app:group_edit', args=[self.group.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'group_management/group_form.html')
        self.assertIn('group_form', response.context)
        self.assertIn('profile_form', response.context)

    def test_group_edit_view_post(self):
        """グループ編集のPOSTリクエストテスト"""
        response = self.client.post(reverse('agri_app:group_edit', args=[self.group.id]), {
            'name': 'Updated Group',
            'description': 'Updated description',
            'is_active': True,
            'color': '#0000ff'
        })
        self.assertRedirects(response, reverse('agri_app:group_detail', args=[self.group.id]))
        
        # グループが更新されたことを確認
        updated_group = Group.objects.get(id=self.group.id)
        self.assertEqual(updated_group.name, 'Updated Group')
        self.assertEqual(updated_group.groupprofile.description, 'Updated description')

    def test_group_delete_view_get(self):
        """グループ削除確認画面のテスト"""
        response = self.client.get(reverse('agri_app:group_delete', args=[self.group.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'group_management/group_confirm_delete.html')

    def test_group_delete_view_post(self):
        """グループ削除のテスト"""
        response = self.client.post(reverse('agri_app:group_delete', args=[self.group.id]))
        self.assertRedirects(response, reverse('agri_app:group_list'))
        
        # グループが削除されたことを確認
        with self.assertRaises(Group.DoesNotExist):
            Group.objects.get(id=self.group.id)

    def test_group_members_view_get(self):
        """グループメンバー管理画面のGETリクエストテスト"""
        response = self.client.get(reverse('agri_app:group_members', args=[self.group.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'group_management/group_members.html')
        self.assertIn('member_form', response.context)

    def test_group_members_view_post(self):
        """グループメンバー更新のテスト"""
        user2 = User.objects.create_user(username='user2', password='pass2')
        response = self.client.post(reverse('agri_app:group_members', args=[self.group.id]), {
            'users': [self.user.id, user2.id]
        })
        self.assertRedirects(response, reverse('agri_app:group_detail', args=[self.group.id]))
        
        # メンバーが更新されたことを確認
        self.assertEqual(self.group.user_set.count(), 2)
        self.assertIn(self.user, self.group.user_set.all())
        self.assertIn(user2, self.group.user_set.all())


class ProfileViewsTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username='testuser', password='testpass123')

    def test_profile_view(self):
        """プロフィール表示画面のテスト"""
        response = self.client.get(reverse('agri_app:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile/profile.html')
        self.assertEqual(response.context['user'], self.user)

    def test_profile_edit_view_get(self):
        """プロフィール編集画面のGETリクエストテスト"""
        response = self.client.get(reverse('agri_app:profile_edit'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile/profile_edit.html')
        self.assertIn('form', response.context)

    def test_profile_edit_view_post(self):
        """プロフィール編集のPOSTリクエストテスト"""
        response = self.client.post(reverse('agri_app:profile_edit'), {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com'
        })
        self.assertRedirects(response, reverse('agri_app:profile'))
        
        # プロフィールが更新されたことを確認
        updated_user = User.objects.get(id=self.user.id)
        self.assertEqual(updated_user.first_name, 'Updated')
        self.assertEqual(updated_user.last_name, 'Name')

    def test_password_change_view_get(self):
        """パスワード変更画面のGETリクエストテスト"""
        response = self.client.get(reverse('agri_app:password_change'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile/password_change.html')
        self.assertIn('form', response.context)

    def test_password_change_view_post(self):
        """パスワード変更のPOSTリクエストテスト"""
        response = self.client.post(reverse('agri_app:password_change'), {
            'old_password': 'testpass123',
            'new_password1': 'newpass123',
            'new_password2': 'newpass123'
        })
        self.assertRedirects(response, reverse('agri_app:profile'))
        
        # パスワードが変更されたことを確認
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass123'))


class PasswordResetViewsTest(BaseTestCase):
    def test_password_reset_view_get(self):
        """パスワードリセット画面のGETリクエストテスト"""
        response = self.client.get(reverse('agri_app:password_reset'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password_reset/password_reset_form.html')

    @patch('agri_app.views.send_mail')
    def test_password_reset_view_post(self, mock_send_mail):
        """パスワードリセットのPOSTリクエストテスト"""
        mock_send_mail.return_value = 1
        response = self.client.post(reverse('agri_app:password_reset'), {
            'email': 'test@example.com'
        })
        self.assertRedirects(response, reverse('agri_app:password_reset_done'))

    def test_password_reset_done_view(self):
        """パスワードリセット完了画面のテスト"""
        response = self.client.get(reverse('agri_app:password_reset_done'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password_reset/password_reset_done.html')

    def test_password_reset_confirm_view_invalid_token(self):
        """無効なトークンでのパスワードリセット確認テスト"""
        response = self.client.get(reverse('agri_app:password_reset_confirm', kwargs={
            'uidb64': 'invalid',
            'token': 'invalid'
        }))
        self.assertRedirects(response, reverse('agri_app:password_reset'))

    def test_password_reset_complete_view(self):
        """パスワードリセット完了画面のテスト"""
        response = self.client.get(reverse('agri_app:password_reset_complete'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'password_reset/password_reset_complete.html')


class S3FileManagementViewsTest(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username='testuser', password='testpass123')

    @patch('agri_app.views.list_s3_files')
    def test_s3_file_list_view_get(self, mock_list_files):
        """S3ファイル一覧画面のGETリクエストテスト"""
        mock_list_files.return_value = [
            {'key': 'test1.jpg', 'size': 1024, 'last_modified': '2023-01-01'},
            {'key': 'test2.jpg', 'size': 2048, 'last_modified': '2023-01-02'}
        ]
        
        response = self.client.get(reverse('agri_app:s3_file_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 's3_file_list.html')
        self.assertIn('files', response.context)
        self.assertIn('form', response.context)
        self.assertEqual(len(response.context['files']), 2)

    @patch('agri_app.views.upload_file_to_s3')
    def test_s3_file_upload(self, mock_upload):
        """S3ファイルアップロードのテスト"""
        mock_upload.return_value = True
        
        # テスト用のファイルを作成
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            tmp_file.write(b'test file content')
            tmp_file.flush()
            
            with open(tmp_file.name, 'rb') as file:
                response = self.client.post(reverse('agri_app:s3_file_list'), {
                    'file': file
                }, follow=True)
        
        # 一時ファイルを削除
        os.unlink(tmp_file.name)
        
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('アップロード' in str(message) for message in messages))

    @patch('agri_app.views.delete_file_from_s3')
    def test_s3_file_delete(self, mock_delete):
        """S3ファイル削除のテスト"""
        mock_delete.return_value = True
        
        response = self.client.post(reverse('agri_app:s3_file_list'), {
            'delete': True,
            'file_key': 'test.jpg'
        }, follow=True)
        
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('削除' in str(message) for message in messages))

    @patch('agri_app.views.list_s3_files')
    def test_s3_file_list_exception_handling(self, mock_list_files):
        """S3ファイル一覧取得時の例外処理テスト"""
        mock_list_files.side_effect = Exception('S3 error')
        
        response = self.client.get(reverse('agri_app:s3_file_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['files'], [])
        
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('エラー' in str(message) for message in messages))


class ErrorHandlingViewsTest(BaseTestCase):
    def test_404_error_view(self):
        """404エラーページのテスト"""
        response = self.client.get('/nonexistent-page/')
        self.assertEqual(response.status_code, 404)

    def test_500_error_view(self):
        """500エラーページのテスト"""
        response = self.client.get(reverse('agri_app:server_error'))
        self.assertEqual(response.status_code, 500)
        self.assertTemplateUsed(response, '500.html')


class PermissionTests(BaseTestCase):
    def test_user_management_requires_login(self):
        """ユーザー管理機能はログインが必要"""
        self.client.logout()
        
        # ログインしていない状態でアクセス
        response = self.client.get(reverse('agri_app:user_list'))
        self.assertRedirects(response, f"{reverse('agri_app:user_login')}?next={reverse('agri_app:user_list')}")

    def test_group_management_requires_login(self):
        """グループ管理機能はログインが必要"""
        self.client.logout()
        
        # ログインしていない状態でアクセス
        response = self.client.get(reverse('agri_app:group_list'))
        self.assertRedirects(response, f"{reverse('agri_app:user_login')}?next={reverse('agri_app:group_list')}")

    def test_profile_requires_login(self):
        """プロフィール機能はログインが必要"""
        self.client.logout()
        
        # ログインしていない状態でアクセス
        response = self.client.get(reverse('agri_app:profile'))
        self.assertRedirects(response, f"{reverse('agri_app:user_login')}?next={reverse('agri_app:profile')}")

    def test_s3_file_list_requires_login(self):
        """S3ファイル一覧はログインが必要"""
        self.client.logout()
        
        # ログインしていない状態でアクセス
        response = self.client.get(reverse('agri_app:s3_file_list'))
        self.assertRedirects(response, f"{reverse('agri_app:user_login')}?next={reverse('agri_app:s3_file_list')}")


class IntegrationTests(BaseTestCase):
    def test_complete_user_workflow(self):
        """ユーザー関連の完全なワークフローテスト"""
        self.client.login(username='admin', password='adminpass123')
        
        # 1. ユーザー一覧を表示
        response = self.client.get(reverse('agri_app:user_list'))
        self.assertEqual(response.status_code, 200)
        
        # 2. ユーザー詳細を表示
        response = self.client.get(reverse('agri_app:user_detail', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        
        # 3. ユーザーを編集
        response = self.client.post(reverse('agri_app:user_edit', args=[self.user.id]), {
            'username': 'workflowuser',
            'first_name': 'Workflow',
            'last_name': 'User',
            'email': 'workflow@example.com'
        })
        self.assertRedirects(response, reverse('agri_app:user_detail', args=[self.user.id]))

    def test_complete_group_workflow(self):
        """グループ関連の完全なワークフローテスト"""
        self.client.login(username='admin', password='adminpass123')
        
        # 1. グループ一覧を表示
        response = self.client.get(reverse('agri_app:group_list'))
        self.assertEqual(response.status_code, 200)
        
        # 2. グループを作成
        response = self.client.post(reverse('agri_app:group_create'), {
            'name': 'Workflow Group',
            'description': 'Workflow test group',
            'is_active': True,
            'color': '#ff0000'
        })
        self.assertRedirects(response, reverse('agri_app:group_list'))
        
        # 3. 作成されたグループを取得
        new_group = Group.objects.get(name='Workflow Group')
        
        # 4. グループ詳細を表示
        response = self.client.get(reverse('agri_app:group_detail', args=[new_group.id]))
        self.assertEqual(response.status_code, 200)
        
        # 5. グループを編集
        response = self.client.post(reverse('agri_app:group_edit', args=[new_group.id]), {
            'name': 'Updated Workflow Group',
            'description': 'Updated workflow test group',
            'is_active': True,
            'color': '#00ff00'
        })
        self.assertRedirects(response, reverse('agri_app:group_detail', args=[new_group.id])) 