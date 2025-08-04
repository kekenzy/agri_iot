FROM --platform=linux/amd64 python:3.11.3-slim-bullseye

WORKDIR /usr/src/agri_iot

# 環境変数設定
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Tokyo \
    DJANGO_SETTINGS_MODULE=agri_iot.settings.production

# ログディレクトリと静的ファイルディレクトリの作成
RUN mkdir -p /var/log/django /var/www/static /usr/src/agri_iot/staticfiles

# Pythonパッケージのインストール
RUN pip install --upgrade pip pip-tools

# requirements.inをコピーしてrequirements.txtを生成
COPY requirements.in .
RUN pip-compile --output-file=requirements.txt requirements.in

# requirements.txtからパッケージをインストール
RUN pip install -r requirements.txt

# アプリケーションコードをコピー
COPY . .

# 静的ファイルを収集
RUN python manage.py collectstatic --noinput

# ポート8000を公開
EXPOSE 8000

# ヘルスチェック用のエンドポイント（Pythonを使用）
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health/')" || exit 1

# 本番環境用のコマンド
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "agri_iot.wsgi:application"]
