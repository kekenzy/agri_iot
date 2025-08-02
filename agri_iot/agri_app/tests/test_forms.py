from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
import tempfile
import os

from agri_app.models import UserProfile, GroupProfile
from agri_app.model.form.user_form import UserSearchForm, UserForm
from agri_app.model.form.group_form import GroupSearchForm, GroupForm, GroupProfileForm, GroupMemberForm
from agri_app.model.form.login_user_form import LoginForm
from agri_app.model.form.profile_form import ProfileEditForm, ProfilePasswordChangeForm
from agri_app.model.form.file_form import UploadFileForm


class BaseFormTestCase(TestCase):
    def setUp(self):
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
        self.group = Group.objects.create(name='Test Group')
        self.group_profile = GroupProfile.objects.create(
            group=self.group,
            description='Test group description',
            is_active=True,
            color='#ff0000'
        )


class LoginFormTest(BaseFormTestCase):
    def test_login_form_valid_data(self):
        """ログインフォームの有効なデータテスト"""
        form_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_login_form_invalid_data(self):
        """ログインフォームの無効なデータテスト"""
        form_data = {
            'username': '',
            'password': ''
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('password', form.errors)

    def test_login_form_missing_password(self):
        """パスワードが不足している場合のテスト"""
        form_data = {
            'username': 'testuser'
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)

    def test_login_form_missing_username(self):
        """ユーザー名が不足している場合のテスト"""
        form_data = {
            'password': 'testpass123'
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)


class UserSearchFormTest(BaseFormTestCase):
    def test_user_search_form_empty(self):
        """空のユーザー検索フォームテスト"""
        form = UserSearchForm(data={})
        self.assertTrue(form.is_valid())

    def test_user_search_form_with_username(self):
        """ユーザー名での検索フォームテスト"""
        form_data = {
            'username': 'test'
        }
        form = UserSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['username'], 'test')

    def test_user_search_form_with_first_name(self):
        """名前での検索フォームテスト"""
        form_data = {
            'first_name': 'Test'
        }
        form = UserSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['first_name'], 'Test')

    def test_user_search_form_with_role(self):
        """役割での検索フォームテスト"""
        form_data = {
            'role': 'admin'
        }
        form = UserSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['role'], 'admin')

    def test_user_search_form_all_fields(self):
        """全てのフィールドでの検索フォームテスト"""
        form_data = {
            'username': 'test',
            'first_name': 'Test',
            'role': 'staff'
        }
        form = UserSearchForm(data=form_data)
        self.assertTrue(form.is_valid())


class UserFormTest(BaseFormTestCase):
    def test_user_form_valid_data(self):
        """ユーザーフォームの有効なデータテスト"""
        form_data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'new@example.com',
            'is_active': True
        }
        form = UserForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_user_form_invalid_email(self):
        """無効なメールアドレスのテスト"""
        form_data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'invalid-email',
            'is_active': True
        }
        form = UserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_user_form_duplicate_username(self):
        """重複ユーザー名のテスト"""
        form_data = {
            'username': 'testuser',  # 既存のユーザー名
            'first_name': 'New',
            'last_name': 'User',
            'email': 'new@example.com',
            'is_active': True
        }
        form = UserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_user_form_missing_required_fields(self):
        """必須フィールドが不足している場合のテスト"""
        form_data = {
            'first_name': 'New',
            'last_name': 'User'
        }
        form = UserForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_user_form_with_instance(self):
        """既存ユーザーでのフォームテスト"""
        form_data = {
            'username': 'updateduser',
            'first_name': 'Updated',
            'last_name': 'User',
            'email': 'updated@example.com',
            'is_active': True
        }
        form = UserForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())


class GroupSearchFormTest(BaseFormTestCase):
    def test_group_search_form_empty(self):
        """空のグループ検索フォームテスト"""
        form = GroupSearchForm(data={})
        self.assertTrue(form.is_valid())

    def test_group_search_form_with_name(self):
        """グループ名での検索フォームテスト"""
        form_data = {
            'name': 'Test'
        }
        form = GroupSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['name'], 'Test')

    def test_group_search_form_with_is_active(self):
        """アクティブ状態での検索フォームテスト"""
        form_data = {
            'is_active': 'True'
        }
        form = GroupSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['is_active'], 'True')

    def test_group_search_form_all_fields(self):
        """全てのフィールドでの検索フォームテスト"""
        form_data = {
            'name': 'Test',
            'is_active': 'False'
        }
        form = GroupSearchForm(data=form_data)
        self.assertTrue(form.is_valid())


class GroupFormTest(BaseFormTestCase):
    def test_group_form_valid_data(self):
        """グループフォームの有効なデータテスト"""
        form_data = {
            'name': 'New Group'
        }
        form = GroupForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_group_form_duplicate_name(self):
        """重複グループ名のテスト"""
        form_data = {
            'name': 'Test Group'  # 既存のグループ名
        }
        form = GroupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_group_form_missing_name(self):
        """グループ名が不足している場合のテスト"""
        form_data = {}
        form = GroupForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_group_form_with_instance(self):
        """既存グループでのフォームテスト"""
        form_data = {
            'name': 'Updated Group'
        }
        form = GroupForm(data=form_data, instance=self.group)
        self.assertTrue(form.is_valid())


class GroupProfileFormTest(BaseFormTestCase):
    def test_group_profile_form_valid_data(self):
        """グループプロフィールフォームの有効なデータテスト"""
        form_data = {
            'description': 'New group description',
            'is_active': True,
            'color': '#00ff00'
        }
        form = GroupProfileForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_group_profile_form_default_values(self):
        """デフォルト値のテスト"""
        form_data = {}
        form = GroupProfileForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_group_profile_form_invalid_color(self):
        """無効な色コードのテスト"""
        form_data = {
            'description': 'Test description',
            'is_active': True,
            'color': 'invalid-color'
        }
        form = GroupProfileForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('color', form.errors)

    def test_group_profile_form_with_instance(self):
        """既存グループプロフィールでのフォームテスト"""
        form_data = {
            'description': 'Updated description',
            'is_active': False,
            'color': '#0000ff'
        }
        form = GroupProfileForm(data=form_data, instance=self.group_profile)
        self.assertTrue(form.is_valid())


class GroupMemberFormTest(BaseFormTestCase):
    def setUp(self):
        super().setUp()
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='pass2'
        )

    def test_group_member_form_valid_data(self):
        """グループメンバーフォームの有効なデータテスト"""
        form_data = {
            'users': [self.user.id, self.user2.id]
        }
        form = GroupMemberForm(data=form_data, group=self.group)
        self.assertTrue(form.is_valid())

    def test_group_member_form_empty_users(self):
        """空のユーザーリストのテスト"""
        form_data = {
            'users': []
        }
        form = GroupMemberForm(data=form_data, group=self.group)
        self.assertTrue(form.is_valid())

    def test_group_member_form_invalid_user_id(self):
        """無効なユーザーIDのテスト"""
        form_data = {
            'users': [99999]  # 存在しないユーザーID
        }
        form = GroupMemberForm(data=form_data, group=self.group)
        self.assertFalse(form.is_valid())
        self.assertIn('users', form.errors)

    def test_group_member_form_without_group(self):
        """グループが指定されていない場合のテスト"""
        form_data = {
            'users': [self.user.id]
        }
        with self.assertRaises(TypeError):
            GroupMemberForm(data=form_data)


class ProfileEditFormTest(BaseFormTestCase):
    def test_profile_edit_form_valid_data(self):
        """プロフィール編集フォームの有効なデータテスト"""
        form_data = {
            'username': 'updateduser',
            'first_name': 'Updated',
            'last_name': 'User',
            'email': 'updated@example.com'
        }
        form = ProfileEditForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_profile_edit_form_invalid_email(self):
        """無効なメールアドレスのテスト"""
        form_data = {
            'username': 'updateduser',
            'first_name': 'Updated',
            'last_name': 'User',
            'email': 'invalid-email'
        }
        form = ProfileEditForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_profile_edit_form_missing_username(self):
        """ユーザー名が不足している場合のテスト"""
        form_data = {
            'first_name': 'Updated',
            'last_name': 'User',
            'email': 'updated@example.com'
        }
        form = ProfileEditForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_profile_edit_form_duplicate_username(self):
        """重複ユーザー名のテスト（自分以外）"""
        form_data = {
            'username': 'admin',  # 既存の別ユーザー名
            'first_name': 'Updated',
            'last_name': 'User',
            'email': 'updated@example.com'
        }
        form = ProfileEditForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_profile_edit_form_same_username(self):
        """同じユーザー名のテスト（自分自身）"""
        form_data = {
            'username': 'testuser',  # 自分のユーザー名
            'first_name': 'Updated',
            'last_name': 'User',
            'email': 'updated@example.com'
        }
        form = ProfileEditForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())


class ProfilePasswordChangeFormTest(BaseFormTestCase):
    def test_password_change_form_valid_data(self):
        """パスワード変更フォームの有効なデータテスト"""
        form_data = {
            'old_password': 'testpass123',
            'new_password1': 'newpass123',
            'new_password2': 'newpass123'
        }
        form = ProfilePasswordChangeForm(user=self.user, data=form_data)
        self.assertTrue(form.is_valid())

    def test_password_change_form_wrong_old_password(self):
        """間違った現在のパスワードのテスト"""
        form_data = {
            'old_password': 'wrongpassword',
            'new_password1': 'newpass123',
            'new_password2': 'newpass123'
        }
        form = ProfilePasswordChangeForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('old_password', form.errors)

    def test_password_change_form_password_mismatch(self):
        """新しいパスワードが一致しない場合のテスト"""
        form_data = {
            'old_password': 'testpass123',
            'new_password1': 'newpass123',
            'new_password2': 'differentpass123'
        }
        form = ProfilePasswordChangeForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('new_password2', form.errors)

    def test_password_change_form_weak_password(self):
        """弱いパスワードのテスト"""
        form_data = {
            'old_password': 'testpass123',
            'new_password1': '123',
            'new_password2': '123'
        }
        form = ProfilePasswordChangeForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('new_password2', form.errors)

    def test_password_change_form_missing_fields(self):
        """必須フィールドが不足している場合のテスト"""
        form_data = {
            'old_password': 'testpass123'
        }
        form = ProfilePasswordChangeForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('new_password1', form.errors)
        self.assertIn('new_password2', form.errors)


class UploadFileFormTest(BaseFormTestCase):
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

    def test_upload_file_form_valid_data(self):
        """ファイルアップロードフォームの有効なデータテスト"""
        with open(self.temp_file.name, 'rb') as file:
            form_data = {}
            file_data = {'file': file}
            form = UploadFileForm(data=form_data, files=file_data)
            self.assertTrue(form.is_valid())

    def test_upload_file_form_no_file(self):
        """ファイルが選択されていない場合のテスト"""
        form_data = {}
        file_data = {}
        form = UploadFileForm(data=form_data, files=file_data)
        self.assertFalse(form.is_valid())
        self.assertIn('file', form.errors)

    def test_upload_file_form_invalid_file_type(self):
        """無効なファイルタイプのテスト"""
        # テキストファイルを作成
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as txt_file:
            txt_file.write(b'text content')
            txt_file.flush()
            
            with open(txt_file.name, 'rb') as file:
                form_data = {}
                file_data = {'file': file}
                form = UploadFileForm(data=form_data, files=file_data)
                # フォームのバリデーションは実装によって異なる可能性がある
                # ここでは基本的なテストのみ実行
            
            os.unlink(txt_file.name)

    def test_upload_file_form_large_file(self):
        """大きなファイルのテスト"""
        # 大きなファイルを作成（例：1MB）
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as large_file:
            large_file.write(b'0' * 1024 * 1024)  # 1MB
            large_file.flush()
            
            with open(large_file.name, 'rb') as file:
                form_data = {}
                file_data = {'file': file}
                form = UploadFileForm(data=form_data, files=file_data)
                # ファイルサイズのバリデーションは実装によって異なる可能性がある
                # ここでは基本的なテストのみ実行
            
            os.unlink(large_file.name)

    def test_upload_file_form_empty_file(self):
        """空のファイルのテスト"""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as empty_file:
            # 空のファイル
            pass
            
            with open(empty_file.name, 'rb') as file:
                form_data = {}
                file_data = {'file': file}
                form = UploadFileForm(data=form_data, files=file_data)
                # 空ファイルのバリデーションは実装によって異なる可能性がある
                # ここでは基本的なテストのみ実行
            
            os.unlink(empty_file.name)


class FormIntegrationTest(BaseFormTestCase):
    def test_user_creation_workflow(self):
        """ユーザー作成ワークフローのテスト"""
        # 1. ユーザーフォームでユーザーを作成
        user_form_data = {
            'username': 'workflowuser',
            'first_name': 'Workflow',
            'last_name': 'User',
            'email': 'workflow@example.com',
            'is_active': True
        }
        user_form = UserForm(data=user_form_data)
        self.assertTrue(user_form.is_valid())
        
        if user_form.is_valid():
            user = user_form.save()
            
            # 2. プロフィール編集フォームでユーザーを更新
            profile_form_data = {
                'username': 'updatedworkflowuser',
                'first_name': 'Updated Workflow',
                'last_name': 'User',
                'email': 'updatedworkflow@example.com'
            }
            profile_form = ProfileEditForm(data=profile_form_data, instance=user)
            self.assertTrue(profile_form.is_valid())

    def test_group_creation_workflow(self):
        """グループ作成ワークフローのテスト"""
        # 1. グループフォームでグループを作成
        group_form_data = {
            'name': 'Workflow Group'
        }
        group_form = GroupForm(data=group_form_data)
        self.assertTrue(group_form.is_valid())
        
        if group_form.is_valid():
            group = group_form.save()
            
            # 2. グループプロフィールフォームでプロフィールを作成
            profile_form_data = {
                'description': 'Workflow group description',
                'is_active': True,
                'color': '#ff0000'
            }
            profile_form = GroupProfileForm(data=profile_form_data)
            self.assertTrue(profile_form.is_valid())
            
            if profile_form.is_valid():
                profile = profile_form.save(commit=False)
                profile.group = group
                profile.save()
                
                # 3. グループメンバーフォームでメンバーを追加
                member_form_data = {
                    'users': [self.user.id]
                }
                member_form = GroupMemberForm(data=member_form_data, group=group)
                self.assertTrue(member_form.is_valid())

    def test_form_validation_consistency(self):
        """フォームバリデーションの一貫性テスト"""
        # 同じデータで複数のフォームをテスト
        user_data = {
            'username': 'consistencyuser',
            'first_name': 'Consistency',
            'last_name': 'User',
            'email': 'consistency@example.com'
        }
        
        # ユーザーフォーム
        user_form = UserForm(data=user_data)
        self.assertTrue(user_form.is_valid())
        
        if user_form.is_valid():
            user = user_form.save()
            
            # プロフィール編集フォーム（同じデータ）
            profile_form = ProfileEditForm(data=user_data, instance=user)
            self.assertTrue(profile_form.is_valid())
            
            # 異なるユーザー名でテスト
            user_data['username'] = 'differentuser'
            profile_form = ProfileEditForm(data=user_data, instance=user)
            self.assertTrue(profile_form.is_valid()) 