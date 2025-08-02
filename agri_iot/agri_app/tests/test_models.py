from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from agri_app.models import UserProfile, GroupProfile


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            picture='test.jpg'
        )

    def test_user_profile_creation(self):
        """UserProfileが正しく作成されることをテスト"""
        self.assertEqual(self.user_profile.user, self.user)
        self.assertEqual(self.user_profile.picture, 'test.jpg')
        self.assertIsNotNone(self.user_profile.create_at)
        self.assertIsNotNone(self.user_profile.update_at)

    def test_user_profile_str(self):
        """UserProfileの__str__メソッドをテスト"""
        self.assertEqual(str(self.user_profile), 'testuser')

    def test_user_profile_user_relationship(self):
        """UserProfileとUserの関係をテスト"""
        self.assertEqual(self.user.userprofile, self.user_profile)

    def test_user_profile_unique_user(self):
        """UserProfileのユーザー一意性をテスト"""
        # 同じユーザーで2つ目のプロフィールを作成しようとするとエラー
        with self.assertRaises(IntegrityError):
            UserProfile.objects.create(user=self.user)

    def test_user_profile_cascade_delete(self):
        """ユーザー削除時のカスケード削除をテスト"""
        user_id = self.user.id
        profile_id = self.user_profile.id
        
        # ユーザーを削除
        self.user.delete()
        
        # プロフィールも削除されることを確認
        with self.assertRaises(UserProfile.DoesNotExist):
            UserProfile.objects.get(id=profile_id)
        
        # ユーザーも削除されることを確認
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=user_id)

    def test_user_profile_picture_blank(self):
        """UserProfileのpictureフィールドが空でも作成できることをテスト"""
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        profile2 = UserProfile.objects.create(user=user2)
        
        self.assertEqual(profile2.picture, '')
        self.assertIsNotNone(profile2.create_at)

    def test_user_profile_timestamps(self):
        """UserProfileのタイムスタンプをテスト"""
        # 作成時刻が現在時刻に近いことを確認
        now = timezone.now()
        time_diff = abs((now - self.user_profile.create_at).total_seconds())
        self.assertLess(time_diff, 10)  # 10秒以内
        
        # 更新時刻が作成時刻と同じことを確認
        self.assertEqual(self.user_profile.create_at, self.user_profile.update_at)


class GroupProfileModelTest(TestCase):
    def setUp(self):
        self.group = Group.objects.create(name='Test Group')
        self.group_profile = GroupProfile.objects.create(
            group=self.group,
            description='Test group description',
            is_active=True,
            color='#ff0000'
        )

    def test_group_profile_creation(self):
        """GroupProfileが正しく作成されることをテスト"""
        self.assertEqual(self.group_profile.group, self.group)
        self.assertEqual(self.group_profile.description, 'Test group description')
        self.assertTrue(self.group_profile.is_active)
        self.assertEqual(self.group_profile.color, '#ff0000')
        self.assertIsNotNone(self.group_profile.create_at)
        self.assertIsNotNone(self.group_profile.update_at)

    def test_group_profile_str(self):
        """GroupProfileの__str__メソッドをテスト"""
        self.assertEqual(str(self.group_profile), 'Test Group')

    def test_group_profile_group_relationship(self):
        """GroupProfileとGroupの関係をテスト"""
        self.assertEqual(self.group.groupprofile, self.group_profile)

    def test_get_member_count(self):
        """get_member_countメソッドをテスト"""
        user1 = User.objects.create_user(username='user1', password='pass1')
        user2 = User.objects.create_user(username='user2', password='pass2')
        self.group.user_set.add(user1, user2)
        
        self.assertEqual(self.group_profile.get_member_count(), 2)

    def test_get_member_count_empty(self):
        """空のグループのget_member_countメソッドをテスト"""
        self.assertEqual(self.group_profile.get_member_count(), 0)

    def test_get_permissions_display(self):
        """get_permissions_displayメソッドをテスト"""
        # 権限を追加
        from django.contrib.auth.models import Permission
        from django.contrib.contenttypes.models import ContentType
        
        content_type = ContentType.objects.get_for_model(User)
        permission1 = Permission.objects.create(
            codename='test_permission1',
            name='Test Permission 1',
            content_type=content_type
        )
        permission2 = Permission.objects.create(
            codename='test_permission2',
            name='Test Permission 2',
            content_type=content_type
        )
        
        self.group.permissions.add(permission1, permission2)
        
        permissions_display = self.group_profile.get_permissions_display()
        self.assertIn('Test Permission 1', permissions_display)
        self.assertIn('Test Permission 2', permissions_display)

    def test_get_permissions_display_empty(self):
        """権限がない場合のget_permissions_displayメソッドをテスト"""
        permissions_display = self.group_profile.get_permissions_display()
        self.assertEqual(permissions_display, '')

    def test_group_profile_default_values(self):
        """GroupProfileのデフォルト値をテスト"""
        group2 = Group.objects.create(name='Test Group 2')
        group_profile2 = GroupProfile.objects.create(group=group2)
        
        self.assertTrue(group_profile2.is_active)  # デフォルトはTrue
        self.assertEqual(group_profile2.color, '#667eea')  # デフォルトカラー
        self.assertIsNone(group_profile2.description)  # デフォルトはNone

    def test_group_profile_unique_group(self):
        """GroupProfileのグループ一意性をテスト"""
        # 同じグループで2つ目のプロフィールを作成しようとするとエラー
        with self.assertRaises(IntegrityError):
            GroupProfile.objects.create(group=self.group)

    def test_group_profile_cascade_delete(self):
        """グループ削除時のカスケード削除をテスト"""
        group_id = self.group.id
        profile_id = self.group_profile.id
        
        # グループを削除
        self.group.delete()
        
        # プロフィールも削除されることを確認
        with self.assertRaises(GroupProfile.DoesNotExist):
            GroupProfile.objects.get(id=profile_id)
        
        # グループも削除されることを確認
        with self.assertRaises(Group.DoesNotExist):
            Group.objects.get(id=group_id)

    def test_group_profile_color_validation(self):
        """GroupProfileの色コードバリデーションをテスト"""
        # 有効な色コード
        valid_colors = ['#ff0000', '#00ff00', '#0000ff', '#ffffff', '#000000']
        for color in valid_colors:
            group = Group.objects.create(name=f'Group {color}')
            profile = GroupProfile.objects.create(group=group, color=color)
            self.assertEqual(profile.color, color)

    def test_group_profile_timestamps(self):
        """GroupProfileのタイムスタンプをテスト"""
        # 作成時刻が現在時刻に近いことを確認
        now = timezone.now()
        time_diff = abs((now - self.group_profile.create_at).total_seconds())
        self.assertLess(time_diff, 10)  # 10秒以内
        
        # 更新時刻が作成時刻と同じことを確認
        self.assertEqual(self.group_profile.create_at, self.group_profile.update_at)

    def test_group_profile_is_active_filter(self):
        """GroupProfileのis_activeフィルタをテスト"""
        # アクティブなグループ
        active_group = Group.objects.create(name='Active Group')
        active_profile = GroupProfile.objects.create(
            group=active_group,
            is_active=True
        )
        
        # 非アクティブなグループ
        inactive_group = Group.objects.create(name='Inactive Group')
        inactive_profile = GroupProfile.objects.create(
            group=inactive_group,
            is_active=False
        )
        
        # アクティブなグループのみを取得
        active_groups = Group.objects.filter(groupprofile__is_active=True)
        self.assertIn(active_group, active_groups)
        self.assertNotIn(inactive_group, active_groups)


class BaseMetaModelTest(TestCase):
    def test_base_meta_abstract(self):
        """BaseMetaが抽象クラスであることをテスト"""
        from agri_app.models import BaseMeta
        
        # 抽象クラスなので直接インスタンス化できない
        with self.assertRaises(TypeError):
            BaseMeta()

    def test_base_meta_inheritance(self):
        """BaseMetaの継承をテスト"""
        # UserProfileとGroupProfileがBaseMetaを継承していることを確認
        self.assertTrue(hasattr(UserProfile, 'create_at'))
        self.assertTrue(hasattr(UserProfile, 'update_at'))
        self.assertTrue(hasattr(GroupProfile, 'create_at'))
        self.assertTrue(hasattr(GroupProfile, 'update_at'))


class ModelIntegrationTest(TestCase):
    """モデル統合テスト"""

    def test_user_group_integration(self):
        """ユーザーとグループの統合テスト"""
        # ユーザーを作成
        user = User.objects.create_user(
            username='integrationuser',
            email='integration@example.com',
            password='integrationpass123'
        )
        user_profile = UserProfile.objects.create(user=user)
        
        # グループを作成
        group = Group.objects.create(name='Integration Group')
        group_profile = GroupProfile.objects.create(
            group=group,
            description='Integration test group',
            is_active=True,
            color='#ff00ff'
        )
        
        # ユーザーをグループに追加
        group.user_set.add(user)
        
        # 関連性を確認
        self.assertIn(user, group.user_set.all())
        self.assertIn(group, user.groups.all())
        self.assertEqual(group_profile.get_member_count(), 1)
        
        # プロフィールの関連性を確認
        self.assertEqual(user.userprofile, user_profile)
        self.assertEqual(group.groupprofile, group_profile)

    def test_bulk_operations(self):
        """一括操作のテスト"""
        # 複数のユーザーを作成
        users = []
        for i in range(5):
            user = User.objects.create_user(
                username=f'bulkuser{i}',
                email=f'bulk{i}@example.com',
                password=f'bulkpass{i}'
            )
            UserProfile.objects.create(user=user)
            users.append(user)
        
        # 複数のグループを作成
        groups = []
        for i in range(3):
            group = Group.objects.create(name=f'Bulk Group {i}')
            GroupProfile.objects.create(
                group=group,
                description=f'Bulk test group {i}',
                is_active=True,
                color=f'#{i:06x}'
            )
            groups.append(group)
        
        # ユーザーをグループに一括追加
        for group in groups:
            group.user_set.add(*users)
        
        # 結果を確認
        for group in groups:
            self.assertEqual(group.groupprofile.get_member_count(), 5)
        
        for user in users:
            self.assertEqual(user.groups.count(), 3)

    def test_model_queries(self):
        """モデルクエリのテスト"""
        # テストデータを作成
        users = []
        for i in range(10):
            user = User.objects.create_user(
                username=f'queryuser{i}',
                email=f'query{i}@example.com',
                password=f'querypass{i}'
            )
            UserProfile.objects.create(user=user)
            users.append(user)
        
        group = Group.objects.create(name='Query Test Group')
        GroupProfile.objects.create(
            group=group,
            description='Query test group',
            is_active=True
        )
        
        # ユーザーをグループに追加
        group.user_set.add(*users[:5])  # 最初の5人を追加
        
        # クエリテスト
        # 1. プロフィールを持つユーザーを取得
        users_with_profiles = User.objects.select_related('userprofile').all()
        self.assertEqual(users_with_profiles.count(), 10)
        
        # 2. グループメンバーを取得
        group_members = group.user_set.all()
        self.assertEqual(group_members.count(), 5)
        
        # 3. アクティブなグループを取得
        active_groups = Group.objects.filter(groupprofile__is_active=True)
        self.assertIn(group, active_groups)
        
        # 4. 特定の色のグループを取得
        red_groups = Group.objects.filter(groupprofile__color='#ff0000')
        # このテストでは赤いグループは作成していないので0
        self.assertEqual(red_groups.count(), 0)

    def test_model_constraints(self):
        """モデル制約のテスト"""
        # 1. ユーザー名の一意性
        User.objects.create_user(
            username='constraintuser',
            email='constraint1@example.com',
            password='constraintpass123'
        )
        
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username='constraintuser',  # 重複
                email='constraint2@example.com',
                password='constraintpass123'
            )
        
        # 2. メールアドレスの一意性（設定による）
        # このテストは設定によって異なる可能性がある
        
        # 3. グループ名の一意性
        Group.objects.create(name='Constraint Group')
        
        with self.assertRaises(IntegrityError):
            Group.objects.create(name='Constraint Group')  # 重複

    def test_model_methods(self):
        """モデルメソッドのテスト"""
        # ユーザーを作成
        user = User.objects.create_user(
            username='methoduser',
            email='method@example.com',
            password='methodpass123',
            first_name='Method',
            last_name='User'
        )
        UserProfile.objects.create(user=user)
        
        # グループを作成
        group = Group.objects.create(name='Method Group')
        GroupProfile.objects.create(
            group=group,
            description='Method test group',
            is_active=True,
            color='#00ff00'
        )
        
        # メソッドテスト
        # 1. User.get_full_name()
        self.assertEqual(user.get_full_name(), 'Method User')
        
        # 2. UserProfile.__str__()
        self.assertEqual(str(user.userprofile), 'methoduser')
        
        # 3. GroupProfile.__str__()
        self.assertEqual(str(group.groupprofile), 'Method Group')
        
        # 4. GroupProfile.get_member_count()
        self.assertEqual(group.groupprofile.get_member_count(), 0)
        
        # ユーザーを追加
        group.user_set.add(user)
        self.assertEqual(group.groupprofile.get_member_count(), 1) 