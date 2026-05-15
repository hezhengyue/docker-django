#!/usr/bin/env bash

wait_for_service() {

    local service="$1"
    local timeout="${2:-60}"

    log_info "等待 $service 就绪"

    local count=0

    while true; do

        container_id=$($COMPOSE ps -q "$service")

        [[ -z "$container_id" ]] && {
            sleep 1
            continue
        }

        status=$(
            docker inspect \
            --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}running{{end}}' \
            "$container_id" \
            2>/dev/null
        )

        [[ "$status" == "healthy" || "$status" == "running" ]] && break

        sleep 1
        ((count++))

        if [[ $count -ge $timeout ]]; then
            log_error "$service 启动超时"
            exit 1
        fi
    done

    log_success "$service 已就绪"
}