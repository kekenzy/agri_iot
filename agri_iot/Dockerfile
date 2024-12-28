FROM python:3.11.3-bullseye

WORKDIR /usr/src/agri_iot

# .pyc 生成しない
ENV PYTHONDONTWRITEBYTECODE 1
# 標準出力・標準エラーのストリームバッファリングしない
ENV PYTHONUNBUFFERED 1

# モジュールインストール
RUN apt-get update
RUN apt-get install -y gettext
RUN apt-get install -y vim
RUN apt-get install -y iputils-ping net-tools


RUN apt-get install -y xmlsec1 poppler-utils

# python モジュールインストール
RUN pip install --upgrade pip
# requiremnts.ini のコンパイル
RUN pip install pip-tools
# RUN pip install django-cors-headers
COPY ./requirements.in .
# requiremnts.txt の生成
RUN pip-compile
# requiremnts.txt のコンパイル
RUN pip install -r requirements.txt

ENV TZ Asia/Tokyo

COPY . .
