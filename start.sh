#!/usr/bin/env bash
# start.sh

set -e

BASE_DIR="$(cd "$(dirname "$0")" && pwd)"

source "$BASE_DIR/scripts/utils.sh"
source "$BASE_DIR/scripts/env.sh"
source "$BASE_DIR/scripts/compose.sh"
source "$BASE_DIR/scripts/service.sh"
source "$BASE_DIR/scripts/django.sh"
source "$BASE_DIR/scripts/local.sh"

case "${1:-help}" in

    # =========================================================
    # Production
    # =========================================================

    up|start)
        ensure_env
        ensure_cert

        log_info "启动生产环境"

        compose_cmd full up -d
        ;;

    init|setup)
        ensure_env
        ensure_cert

        log_info "初始化生产环境"

        compose_cmd full up -d

        wait_for_service web 60

        run_migrations

        MANAGE collectstatic --noinput

        ensure_superuser

        $COMPOSE restart web celery celery-beat

        log_success "初始化完成"
        ;;

    update)
        ensure_env

        log_info "更新生产环境"

        compose_cmd full build --no-cache web celery celery-beat

        compose_cmd full up -d

        wait_for_service web 60

        run_migrations

        MANAGE collectstatic --noinput

        $COMPOSE restart web celery celery-beat

        log_success "更新完成"
        ;;

    down|stop)
        compose_cmd full down --remove-orphans
        ;;

    restart)
        compose_cmd full down --remove-orphans
        compose_cmd full up -d
        ;;

    rebuild)
        compose_cmd full up -d --build
        ;;

    logs)
        [[ -n "$2" ]] \
            && $COMPOSE logs -f "$2" \
            || $COMPOSE logs -f $SERVICES_FULL
        ;;

    exec)
        container="${2:-web}"
        shell="${3:-bash}"

        $COMPOSE exec "$container" "$shell"
        ;;

    # =========================================================
    # Local Development
    # =========================================================

    dev)
        run_local_dev
        ;;

    dev:up)
        ensure_env
        compose_cmd dev up -d
        ;;

    dev:down)
        compose_cmd dev down
        ;;

    dev:logs)
        [[ -n "$2" ]] \
            && $COMPOSE logs -f "$2" \
            || $COMPOSE logs -f $SERVICES_DEV
        ;;

    dev:ps)
        compose_cmd dev ps
        ;;

    dev:sync)
        enter_local_env
        run_migrations
        ;;

    # =========================================================
    # Django Commands
    # =========================================================

    migrate)
        enter_local_env
        MANAGE migrate
        ;;

    makemigrations)
        enter_local_env
        MANAGE makemigrations
        ;;

    superuser)
        enter_local_env
        MANAGE createsuperuser
        ;;

    shell)
        enter_local_env
        MANAGE shell
        ;;

    # =========================================================
    # Clean
    # =========================================================

    clean)
        compose_cmd full down -v --remove-orphans
        ;;

    clean:pycache)
        clean_pycache ./django
        ;;

    help|--help|-h|*)
        show_help
        ;;

esac