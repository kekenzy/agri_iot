def show_debug_toolbar(request):
    """
    リクエストヘッダよりDebug Tool Bar表示有無を取得する。
    :param request:
    :return: boolean
    """
    # リクエストに「X-DEV-CP-DEBUG-TOOLBAR」が入っている場合DDTを表示する
    if request.META.get('HTTP_X_DEV_CP_DEBUG_TOOLBAR'):
        return True
    else:
        return False


def set_debug_toolbar(use_debug_tool_bar, installed_apps, middleware):
    """
    Debug Tool Barの表示の設定を行う。
    :param use_debug_tool_bar:
    :param installed_apps:
    :param middleware:
    """
    if use_debug_tool_bar:
        # INSTALLED_APPSに追加
        installed_apps.append('debug_toolbar')

        # MIDDLEWAREに追加
        target_middleware = 'django.middleware.clickjacking.XFrameOptionsMiddleware'  # このミドルウェアの後に入れる
        ddt_middleware = 'debug_toolbar.middleware.DebugToolbarMiddleware'  # Django Debug Toolbar
        if target_middleware in middleware:
            # 順番が重要のため、target_middleの直後に挿入
            i = middleware.index(target_middleware)
            middleware.insert(i + 1, ddt_middleware)
        else:
            # 見つからない場合はエラー
            raise 'MiddlewareにXFrameOptionsMiddlewareが設定されていません'
    return
