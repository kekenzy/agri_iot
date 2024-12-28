from datetime import datetime
from zoneinfo import ZoneInfo


def datetime_now_utc():
    """
    システム日時(UTC)取得
    :return: datetime (with timezone)
    """
    return datetime.now(ZoneInfo("UTC"))


def datetime_now_jst():
    """
    システム日時(JST)取得
    :return: datetime (with timezone)
    """
    return datetime.now(ZoneInfo("Asia/Tokyo"))


def format_jst_datetime(dt):
    """
    JSTかつ日時文字列に整形
    :param dt awareなdatetime
    :return: str
    """
    if not dt:
        # Noneの場合処理終了
        return dt

    jst_datetime = dt.astimezone(ZoneInfo("Asia/Tokyo"))
    date_format = "%Y年%-m月%-d日 %-H時%-M分"

    return jst_datetime.strftime(date_format)
