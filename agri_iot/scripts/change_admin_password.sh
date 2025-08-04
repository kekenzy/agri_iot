#!/bin/bash

echo "🔑 AWSのDjangoのadminユーザーのパスワードを変更します..."
echo ""

# 現在のディレクトリを確認
if [ ! -f "manage.py" ]; then
    echo "❌ エラー: manage.pyが見つかりません"
    echo "💡 agri_iotディレクトリで実行してください"
    exit 1
fi

# Djangoの管理コマンドを使用してパスワードを変更
echo "🔄 adminユーザーのパスワードを「Kekenji1」に変更中..."
python3 manage.py change_admin_password --username admin --password Kekenji1

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ パスワードの変更が完了しました！"
    echo ""
    echo "📋 ログイン情報:"
    echo "👤 ユーザー名: admin"
    echo "🔑 パスワード: Kekenji1"
    echo ""
    echo "🌐 AWSのDjangoのadmin画面にアクセスしてログインしてください"
else
    echo ""
    echo "❌ パスワードの変更に失敗しました"
    echo "💡 adminユーザーが存在することを確認してください"
    exit 1
fi 