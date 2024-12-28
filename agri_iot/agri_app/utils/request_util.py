import woothee


def get_request_info(request):
    """
    リクエスト情報取得処理
    HttpRequestから一般的なリクエスト情報を取得する
    :param request: HttpRequest
    :return: request_info: dict
    """
    # ソースIPアドレス
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    x_client_souce = request.META.get("HTTP_X_CLIENT_SOURCE")
    if x_forwarded_for:
        # クライアントIPとプロキシサーバーIPとカンマ区切りになっている可能性あり
        ip_address = x_forwarded_for.split(",")[0]
    elif x_client_souce:
        ip_address = x_client_souce
    else:
        ip_address = request.META.get("REMOTE_ADDR")

    request_info = {
        "referrer": request.META.get("HTTP_REFERER"),
        "request_method": request.META.get("REQUEST_METHOD"),
        "request_url": request.path_info,
        "source_ip_address": ip_address,
        "user_agent": request.META.get("HTTP_USER_AGENT"),
    }

    return request_info


def parse_user_agent(user_agent):
    """
    User Agent変換処理
    User Agentをカテゴリ毎に判定して変換
    :param user_agent: str
    :return: parsed_user_agent: dict
    """
    parsed_data = woothee.parse(user_agent)
    return {
        "category": parsed_data["category"],
        "name": parsed_data["name"],
        "version": parsed_data["version"],
        "os": parsed_data["os"],
        "vendor": parsed_data["vendor"],
        "os_version": parsed_data["os_version"],
    }


