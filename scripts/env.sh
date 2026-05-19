#!/usr/bin/env bash
# scripts/env.sh

SERVICES_FULL="db redis celery celery-beat web nginx"
SERVICES_DEV="db redis"

APPS_LIST="core jobs"

PRIORITY_APP="${PRIORITY_APP:-${APPS_LIST%% *}}"

ensure_env() {

    [[ -f .env ]] && return

    if [[ -f .env.example ]]; then
        cp .env.example .env
        log_warn "已自动创建 .env"
    else
        log_error "缺少 .env 文件"
        exit 1
    fi
}

ensure_cert() {

    mkdir -p nginx/ssl

    [[ -f nginx/ssl/fullchain.pem && -f nginx/ssl/privkey.pem ]] && return

    log_info "生成 SSL 证书"

    openssl req -x509 -nodes -days 3650 \
        -newkey rsa:2048 \
        -keyout nginx/ssl/privkey.pem \
        -out nginx/ssl/fullchain.pem \
        -subj "/C=CN/ST=Beijing/L=Beijing/O=Dev/CN=localhost" \
        2>/dev/null

    chmod 600 nginx/ssl/privkey.pem

    log_success "SSL 证书生成完成"
}