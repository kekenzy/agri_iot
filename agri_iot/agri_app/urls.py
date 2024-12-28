from django.urls import path, include, re_path

from . import views
from django.conf import settings
import debug_toolbar  # 追加

app_name = "agri_app"

urlpatterns = [
    path("", views.index, name="index"),
]

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^__debug__/', include(debug_toolbar.urls)),
    ]
