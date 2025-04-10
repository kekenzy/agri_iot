from django.urls import path, include, re_path

from . import views
from django.conf import settings
import debug_toolbar  # 追加

app_name = "agri_app"

urlpatterns = [
    path("", views.index, name="index"),
    path("user_login", views.user_login, name="user_login"),
    path("user_logout", views.user_logout, name="user_logout"),
    path("home", views.home, name="home"),
]
