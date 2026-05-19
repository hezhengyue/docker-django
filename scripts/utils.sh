#!/usr/bin/env bash
# scripts/utils.sh

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

log_warn() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

clean_pycache() {
    local base_dir="${1:-.}"

    find "$base_dir" \
        -type d \
        -name "__pycache__" \
        -exec rm -rf {} + 2>/dev/null || true

    log_success "Pycache 清理完成"
}

show_help() {
cat << EOF

Django + Docker CLI

Production:
  up/start
  init/setup
  update
  down/stop
  restart
  rebuild

Development:
  dev
  dev:up
  dev:down
  dev:sync

Django:
  migrate
  makemigrations
  shell
  superuser

Cleanup:
  clean
  clean:pycache

EOF
}