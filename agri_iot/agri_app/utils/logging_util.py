import functools
import inspect
import logging
import threading

import uuid
from os.path import basename
from pprint import pformat

logger = logging.getLogger('application')
thread_local = threading.local()


class CustomLogManager:
    CUSTOM_LOG_PARAMS = "customer_log_param"

    @classmethod
    def get(cls):
        """
        セッションID、リクエストIDを取得する。
        :return: str
        """
        if not hasattr(thread_local, cls.CUSTOM_LOG_PARAMS):
            setattr(thread_local, cls.CUSTOM_LOG_PARAMS, {})
        return getattr(thread_local, cls.CUSTOM_LOG_PARAMS)

    @classmethod
    def set(cls, session_key):
        """
        セッションID、リクエストIDを設定する。
        :param session_key:
        """
        # uuid先頭8桁を使用
        custom_log_params = {
            "session_id": session_key[:8],
            "request_id": str(uuid.uuid4())[:8]
        }

        setattr(thread_local, cls.CUSTOM_LOG_PARAMS, custom_log_params)


class SessionIdFilter(logging.Filter):
    def filter(self, record):
        """
        ログ用カスタムFilter
        settingsのLoggingのfilterに設定する。
        :param record:
        :return:
        """
        custom_log_params = CustomLogManager.get()
        record.session_id = custom_log_params.get("session_id", "")
        return True


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        """
        ログ用カスタムFilter
        settingsのLoggingのfilterに設定する。
        :param record:
        :return:
        """
        custom_log_params = CustomLogManager.get()
        record.request_id = custom_log_params.get("request_id", "")
        return True


class CustomFormatter(logging.Formatter):
    def format(self, record):
        """
        log_decorator用のフォーマッタ
        何もしないと全てlog_decoratorのファイル名と行番号が表示されるため、
        デコレータ呼び出し元関数のファイル名と行番号に置き換える。
        :param record:
        :return:
        """
        extra = getattr(record, "__dict__", {})
        if extra.get("real_filename"):
            record.filename = extra.pop("real_filename")
        if extra.get("real_lineno"):
            record.lineno = extra.pop("real_lineno")

        return super().format(record)


def make_extra_info_for_logger(func):
    """
    呼び出し元関数のファイル名、行番号を取得しloggerのextraのdictを作成する。
    :param func:
    :return: dict
    """
    # 関数からファイル名、行番号を取得
    file_path = inspect.getfile(func)
    lineno = inspect.getsourcelines(func)[1]

    # loggerに引き渡す呼び出し元の情報
    extra = {
        'real_filename': basename(file_path),
        'real_lineno': lineno,
    }
    return extra


def log_decorator(func_name_jp=""):
    """
    共通的に処理開始・終了のログ出力を行うデコレータ。
    引数あれば処理関数名としてログに出力する。
    :param func_name_jp:
    :return:
    """

    def _log_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # パラメータで処理名が渡されたら半角スペース追加
            param = f"{func_name_jp} " if func_name_jp else ""

            func_name = func.__name__
            extra = make_extra_info_for_logger(func)

            # # 呼び出し元ファイル[行数]を出力する
            frame_obj = inspect.currentframe().f_back
            logger.debug(f"[{func_name}] 呼出元 {frame_obj.f_code.co_filename}:{frame_obj.f_lineno}", extra=extra)

            try:
                # 開始ログを出力する
                logger.info(f"[{func_name}] {param}処理開始", extra=extra)
                logger.debug(f"args : {pformat(args)}", extra=extra)
                logger.debug(f"kwargs : {pformat(kwargs)}", extra=extra)

                ret = func(*args, **kwargs)

                # 終了ログを出力する
                logger.info(f"[{func_name}] {param}処理終了", extra=extra)

                return ret

            except Exception as e:
                # エラー発生ログを出力する
                logger.info(f"{param} exception", extra=extra)
                logger.error(e, extra=extra)
                raise e

        return wrapper
    return _log_decorator


def log_decorator_for_test(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # 関数等取得
        func_name = func.__name__
        extra = make_extra_info_for_logger(func)

        try:
            # 開始ログを出力する
            logger.info(f"---- start {func_name} ----".ljust(64, "-"), extra=extra)

            ret = func(*args, **kwargs)

            # 終了ログを出力する
            logger.info(f"---- end {func_name} ----".ljust(64, "-"), extra=extra)

            return ret

        except Exception as e:
            # エラー発生ログを出力する
            logger.info(f"exception", extra=extra)
            logger.error(e, extra=extra)
            raise e

    return wrapper
