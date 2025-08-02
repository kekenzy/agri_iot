from django.test import TestCase, Client, TransactionTestCase
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages
from django.db import transaction
from unittest.mock import patch, MagicMock
import tempfile
import os

from agri_app.models import UserProfile, GroupProfile


class BaseIntegrationTestCase(TransactionTestCase):
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


class EndToEndWorkflowTest(BaseIntegrationTestCase):
    """エンドツーエンドのワークフローテスト"""

    def test_complete_user_workflow(self):
        """完全なユーザーワークフローのテスト"""
        # 1. ログイン
        response = self.client.post(reverse('agri_app:user_login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertRedirects(response, reverse('agri_app:home'))
        
        # 2. ホーム画面
        response = self.client.get(reverse('agri_app:home'))
        self.assertEqual(response.status_code, 200)
        
        # 3. プロフィール編集
        response = self.client.post(reverse('agri_app:profile_edit'), {
            'username': 'updateduser',
            'first_name': 'Updated',
            'last_name': 'User',
            'email': 'updated@example.com'
        })
        self.assertRedirects(response, reverse('agri_app:profile'))

    def test_complete_admin_workflow(self):
        """完全な管理者ワークフローのテスト"""
        self.client.login(username='admin', password='adminpass123')
        
        # 1. ユーザー管理
        response = self.client.get(reverse('agri_app:user_list'))
        self.assertEqual(response.status_code, 200)
        
        # 2. グループ作成
        response = self.client.post(reverse('agri_app:group_create'), {
            'name': 'Test Group',
            'description': 'Test group',
            'is_active': True,
            'color': '#ff0000'
        })
        self.assertRedirects(response, reverse('agri_app:group_list'))


class DatabaseIntegrationTest(BaseIntegrationTestCase):
    """データベース統合テスト"""

    def test_user_profile_integration(self):
        """ユーザープロフィール統合テスト"""
        new_user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='newpass123'
        )
        
        profile = UserProfile.objects.create(user=new_user)
        self.assertEqual(new_user.userprofile, profile)

    def test_group_profile_integration(self):
        """グループプロフィール統合テスト"""
        group = Group.objects.create(name='Test Group')
        profile = GroupProfile.objects.create(
            group=group,
            description='Test description',
            is_active=True,
            color='#00ff00'
        )
        
        self.assertEqual(group.groupprofile, profile)
        self.assertEqual(profile.get_member_count(), 0)


class APIIntegrationTest(BaseIntegrationTestCase):
    """API統合テスト"""

    def test_form_validation_integration(self):
        """フォームバリデーション統合テスト"""
        from agri_app.model.form.user_form import UserForm
        
        form_data = {
            'username': 'formtestuser',
            'first_name': 'Form Test',
            'last_name': 'User',
            'email': 'formtest@example.com',
            'is_active': True
        }
        
        form = UserForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_s3_integration(self):
        """S3統合テスト"""
        with patch('agri_app.views.list_s3_files') as mock_list:
            mock_list.return_value = []
            self.client.login(username='testuser', password='testpass123')
            response = self.client.get(reverse('agri_app:s3_file_list'))
            self.assertEqual(response.status_code, 200)


class SecurityIntegrationTest(BaseIntegrationTestCase):
    """セキュリティ統合テスト"""

    def test_authentication_required(self):
        """認証が必要なページのテスト"""
        protected_urls = [
            reverse('agri_app:profile'),
            reverse('agri_app:s3_file_list'),
        ]
        
        for url in protected_urls:
            response = self.client.get(url)
            self.assertRedirects(response, f"{reverse('agri_app:user_login')}?next={url}")

    def test_csrf_protection(self):
        """CSRF保護のテスト"""
        response = self.client.post(reverse('agri_app:user_login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 403) 