from django.urls import path, include, re_path

from . import views
from django.conf import settings
import debug_toolbar  # 追加

app_name = "agri_app"

urlpatterns = [
    path("", views.user_login, name="user_login"),
    path("user_login", views.user_login, name="user_login"),
    path("user_logout", views.user_logout, name="user_logout"),
    path("home", views.home, name="home"),
    path("s3_file_list", views.s3_file_list_view, name="s3_file_list"),
    # path('', views.s3_file_list_view, name='s3_file_list'),
    
    # ユーザー管理機能
    path("users", views.user_list, name="user_list"),
    path("users/create", views.user_create, name="user_create"),
    path("users/<int:user_id>", views.user_detail, name="user_detail"),
    path("users/<int:user_id>/edit", views.user_edit, name="user_edit"),
    path("users/<int:user_id>/delete", views.user_delete, name="user_delete"),
    
    # プロフィール機能
    path("profile", views.profile_view, name="profile"),
    path("profile/edit", views.profile_edit, name="profile_edit"),
    path("profile/password", views.password_change, name="password_change"),
    
    # パスワードリセット機能
    path("password_reset", views.password_reset, name="password_reset"),
    path("password_reset/done", views.password_reset_done, name="password_reset_done"),
    path("reset/<uidb64>/<token>", views.password_reset_confirm, name="password_reset_confirm"),
    path("reset/done", views.password_reset_complete, name="password_reset_complete"),
    
    # グループ管理機能
    path("groups", views.group_list, name="group_list"),
    path("groups/create", views.group_create, name="group_create"),
    path("groups/<int:group_id>", views.group_detail, name="group_detail"),
    path("groups/<int:group_id>/edit", views.group_edit, name="group_edit"),
    path("groups/<int:group_id>/delete", views.group_delete, name="group_delete"),
    path("groups/<int:group_id>/members", views.group_members, name="group_members"),
]
