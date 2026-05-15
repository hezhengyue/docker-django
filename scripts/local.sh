#!/usr/bin/env bash

# =============================================================================
# 🧑‍💻 Enter Local Python Environment
# =============================================================================

enter_local_env() {

    # Docker 模式不需要进入本地环境
    if is_docker_mode; then
        return
    fi

    cd django || exit 1

    if [[ ! -f ".venv/bin/activate" ]]; then
        log_error "Python 虚拟环境不存在"

        log_warn "请先执行："
        echo "./start.sh dev"

        exit 1
    fi

    source .venv/bin/activate
}


# =============================================================================
# 🚀 Local Development
# =============================================================================

run_local_dev() {

    ensure_env

    log_info "启动开发基础设施"

    compose_cmd dev up -d

    wait_for_service db 60
    wait_for_service redis 60

    cd django || exit 1

    # =========================================================================
    # Python Virtual Environment
    # =========================================================================

    if [[ ! -d ".venv" ]]; then

        log_info "创建 Python 虚拟环境"

        python3 -m venv .venv
    fi

    source .venv/bin/activate

    # =========================================================================
    # Install Dependencies
    # =========================================================================

    log_info "安装 Python 依赖"

    PIP install -q --upgrade pip
    PIP install -q -r requirements.txt
    PIP install -q watchdog

    # =========================================================================
    # Django Init
    # =========================================================================

    run_migrations

    ensure_superuser

    # =========================================================================
    # Development Info
    # =========================================================================

    echo ""
    log_success "开发环境启动完成"
    echo ""

    echo "🌐 Django:  http://127.0.0.1:8000"
    echo "🔐 Admin:   http://127.0.0.1:8000/admin"
    echo "🧵 Celery:  Auto Reload Enabled"

    echo ""

    # =========================================================================
    # Process Cleanup
    # =========================================================================

    trap 'kill 0' EXIT

    # =========================================================================
    # 🚀 Django Daphne ASGI Server (替换 runserver)
    # =========================================================================

    daphne -b 127.0.0.1 -p 8000 config.asgi:application &

    # =========================================================================
    # Celery Worker Hot Reload
    # =========================================================================

    WATCHMEDO auto-restart \
        --directory=. \
        --pattern="*.py" \
        --recursive \
        --ignore-patterns="*/logs/*;*/media/*;*/staticfiles/*;*/__pycache__/*;*/.venv/*;*/.git/*" \
        -- \
        celery -A config worker \
        -l info \
        --pool=solo &

    # =========================================================================
    # Celery Beat Hot Reload
    # =========================================================================

    WATCHMEDO auto-restart \
        --directory=. \
        --pattern="*.py" \
        --recursive \
        --ignore-patterns="*/logs/*;*/media/*;*/staticfiles/*;*/__pycache__/*;*/.venv/*;*/.git/*" \
        -- \
        celery -A config beat \
        -l info &

    wait
}