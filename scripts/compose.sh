#!/usr/bin/env bash
# scripts/compose.sh

# =============================================================================
# 🐳 Docker Compose Detection
# =============================================================================

if command -v docker &>/dev/null && docker compose version &>/dev/null 2>&1; then
    COMPOSE="docker compose"
elif command -v docker-compose &>/dev/null; then
    COMPOSE="docker-compose"
else
    log_error "Docker Compose 未安装"
    exit 1
fi

# =============================================================================
# 🔍 Container Status
# =============================================================================

container_running() {

    local service="$1"

    $COMPOSE ps "$service" 2>/dev/null | grep -q "Up"
}

# =============================================================================
# 🌍 Dynamic Runtime Mode
# =============================================================================
# 不使用 ENV_MODE/RUN_MODE 静态变量
# 每次执行动态判断
# =============================================================================

is_docker_mode() {

    container_running web
}

# =============================================================================
# 🐍 Runtime Wrappers
# =============================================================================

PYTHON() {

    if is_docker_mode; then
        $COMPOSE exec -T web python "$@"
    else
        python "$@"
    fi
}

PIP() {

    if is_docker_mode; then
        $COMPOSE exec -T web pip "$@"
    else
        pip "$@"
    fi
}

CELERY() {

    if is_docker_mode; then
        $COMPOSE exec -T web celery "$@"
    else
        celery "$@"
    fi
}

MANAGE() {

    if is_docker_mode; then
        $COMPOSE exec -T web python manage.py "$@"
    else
        python manage.py "$@"
    fi
}

WATCHMEDO() {

    if is_docker_mode; then
        $COMPOSE exec -T web watchmedo "$@"
    else
        watchmedo "$@"
    fi
}

# =============================================================================
# 🐳 Unified Compose Command
# =============================================================================

compose_cmd() {

    local mode="$1"
    shift

    local cmd="$1"
    shift

    local services

    case "$mode" in
        full)
            services="$SERVICES_FULL"
            ;;
        dev)
            services="$SERVICES_DEV"
            ;;
        *)
            log_error "未知 compose mode: $mode"
            exit 1
            ;;
    esac

    case "$cmd" in
        down|config|port|exec|run|logs|ps)
            $COMPOSE "$cmd" "$@"
            ;;
        *)
            $COMPOSE "$cmd" "$@" $services
            ;;
    esac
}