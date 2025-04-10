"""
URL configuration for agri_iot project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from agri_app import views
from django.conf import settings
import debug_toolbar  # 追加


urlpatterns = [
    path('admin/', admin.site.urls),
    path("agri_app/", include("agri_app.urls")),
    # path("__debug__/", include("debug_toolbar.urls")),
]

urlpatterns += staticfiles_urlpatterns()

handler404 = views.page_not_found
handler500 = views.server_error

# 追加  '__debug__/'は他のURLに影響を及ぼさないならなんでも良い
if settings.DEBUG:
    # デバッグツールバー
    print('debug true')
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]