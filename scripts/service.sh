# scripts/service.sh
wait_for_service() {

    local service="$1"
    local timeout="${2:-60}"
    local count=0

    log_info "等待 $service 就绪"

    while true; do

        container_id=$($COMPOSE ps -q "$service")

        if [[ -z "$container_id" ]]; then
            sleep 1
            ((count++))
            [[ $count -ge $timeout ]] && {
                log_error "$service 未找到容器"
                exit 1
            }
            continue
        fi

        running=$(docker inspect --format='{{.State.Running}}' "$container_id" 2>/dev/null)

        if [[ "$running" != "true" ]]; then
            log_error "$service 容器未运行（可能已退出）"
            docker logs "$container_id" --tail 30
            exit 1
        fi

        health=$(docker inspect \
          --format='{{if .State.Health}}{{.State.Health.Status}}{{end}}' \
          "$container_id" 2>/dev/null)

        # ✅ 关键修复：允许 starting
        if [[ "$health" == "healthy" || "$health" == "starting" || -z "$health" ]]; then
            log_success "$service 已就绪"
            break
        fi

        sleep 1
        ((count++))

        if [[ $count -ge $timeout ]]; then
            log_error "$service 启动超时"
            docker logs "$container_id" --tail 30
            exit 1
        fi
    done
}