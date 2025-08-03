#!/bin/bash

# Docker上でテストを実行するスクリプト

set -e

# 色付きの出力用
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ヘルプメッセージ
show_help() {
    echo "使用方法: $0 [オプション]"
    echo ""
    echo "オプション:"
    echo "  --all              全てのテストを実行"
    echo "  --models           モデルテストのみ実行"
    echo "  --views            ビューテストのみ実行"
    echo "  --forms            フォームテストのみ実行"
    echo "  --utils            ユーティリティテストのみ実行"
    echo "  --integration      統合テストのみ実行"
    echo "  --coverage         カバレッジ付きでテスト実行"
    echo "  --verbose          詳細出力でテスト実行"
    echo "  --help             このヘルプを表示"
    echo ""
    echo "例:"
    echo "  $0 --all"
    echo "  $0 --models --coverage"
    echo "  $0 --views --verbose"
}

# テスト実行関数
run_tests() {
    local test_command="$1"
    local description="$2"
    
    echo -e "${BLUE}=== $description ===${NC}"
    echo "実行コマンド: $test_command"
    echo ""
    
    if docker-compose exec agri_iot bash -c "$test_command"; then
        echo -e "${GREEN}✓ $description が成功しました${NC}"
        echo ""
        return 0
    else
        echo -e "${RED}✗ $description が失敗しました${NC}"
        echo ""
        return 1
    fi
}

# メイン処理
main() {
    # 引数がない場合はヘルプを表示
    if [ $# -eq 0 ]; then
        show_help
        exit 1
    fi
    
    # オプション解析
    local test_type=""
    local coverage_flag=""
    local verbose_flag=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --all)
                test_type="all"
                shift
                ;;
            --models)
                test_type="models"
                shift
                ;;
            --views)
                test_type="views"
                shift
                ;;
            --forms)
                test_type="forms"
                shift
                ;;
            --utils)
                test_type="utils"
                shift
                ;;
            --integration)
                test_type="integration"
                shift
                ;;
            --coverage)
                coverage_flag="--coverage"
                shift
                ;;
            --verbose)
                verbose_flag="-v 2"
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                echo -e "${RED}エラー: 不明なオプション '$1'${NC}"
                show_help
                exit 1
                ;;
        esac
    done
    
    # テストコマンドの構築
    local base_command="python manage.py test"
    
    if [ -n "$coverage_flag" ]; then
        base_command="coverage run --source='.' manage.py test"
    fi
    
    if [ -n "$verbose_flag" ]; then
        base_command="$base_command $verbose_flag"
    fi
    
    # テストタイプに応じたコマンド実行
    case $test_type in
        all)
            run_tests "$base_command agri_app.tests" "全てのテスト"
            ;;
        models)
            run_tests "$base_command agri_app.tests.test_models" "モデルテスト"
            ;;
        views)
            run_tests "$base_command agri_app.tests.test_views" "ビューテスト"
            ;;
        forms)
            run_tests "$base_command agri_app.tests.test_forms" "フォームテスト"
            ;;
        utils)
            run_tests "$base_command agri_app.tests.test_utils" "ユーティリティテスト"
            ;;
        integration)
            run_tests "$base_command agri_app.tests.test_integration" "統合テスト"
            ;;
        *)
            echo -e "${RED}エラー: テストタイプが指定されていません${NC}"
            show_help
            exit 1
            ;;
    esac
    
    # カバレッジレポートの表示
    if [ -n "$coverage_flag" ]; then
        echo -e "${BLUE}=== カバレッジレポート ===${NC}"
        docker-compose exec agri_iot coverage report
        echo ""
        
        echo -e "${BLUE}=== HTMLレポートの生成 ===${NC}"
        docker-compose exec agri_iot coverage html
        echo "HTMLレポートが生成されました: htmlcov/index.html"
        echo ""
    fi
    
    echo -e "${GREEN}テスト実行が完了しました${NC}"
}

# スクリプト実行
main "$@" 