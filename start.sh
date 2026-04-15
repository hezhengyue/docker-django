#!/usr/bin/env bash
# start.sh - Django + Docker 开发 CLI（替代 Makefile）
# 用法: ./start.sh <command> [args]
# 示例: ./start.sh up | ./start.sh logs nginx | ./start.sh help

set -e  # 遇到错误立即退出

# 🎨 颜色定义
RED='\033[0;31m' GREEN='\033[0;32m' YELLOW='\033[1;33m' BLUE='\033[0;34m' NC='\033[0m'

# 🐳 自动检测 Docker Compose 命令
COMPOSE="docker compose"
if ! command -v docker &>/dev/null; then
    echo -e "${RED}❌ Docker 未安装${NC}" && exit 1
fi
if ! docker compose version &>/dev/null; then
    if command -v docker-compose &>/dev/null; then
        COMPOSE="docker-compose"
    else
        echo -e "${RED}❌ Docker Compose 未安装${NC}" && exit 1
    fi
fi

# 🔐 自动检查/生成 .env
ensure_env() {
    if [[ ! -f .env ]]; then
        if [[ -f .env.example ]]; then
            cp .env.example .env
            echo -e "${YELLOW}⚠️  已自动创建 .env${NC}"
        else
            echo -e "${RED}❌ 缺少 .env 和 .env.example${NC}" && exit 1
        fi
    fi
}

# 🔑 自动检查/生成 SSL 证书
ensure_cert() {
    mkdir -p nginx/ssl
    if [[ ! -f nginx/ssl/fullchain.pem || ! -f nginx/ssl/privkey.pem ]]; then
        echo -e "${BLUE}🔐 正在生成自签名证书...${NC}"
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout nginx/ssl/privkey.pem \
            -out nginx/ssl/fullchain.pem \
            -subj "/C=CN/ST=Beijing/L=Beijing/O=Dev/CN=localhost" 2>/dev/null
        chmod 600 nginx/ssl/privkey.pem
        echo -e "${GREEN}✅ 证书已生成: nginx/ssl/${NC}"
    fi
}

# 🛠️ 命令路由
case "${1:-help}" in
    up|start)
        ensure_env
        ensure_cert
        echo -e "${BLUE}🚀 启动服务...${NC}"
        $COMPOSE up -d
        sleep 3
        echo -e "\n${GREEN}✅ 服务已启动！${NC}"
        echo -e "  🔐 ${GREEN}https://localhost${NC}"
        echo -e "  🌐 ${GREEN}http://localhost${NC} (自动跳转)"
        echo -e "  💡 首次请运行: ${YELLOW}./start.sh init${NC}"
        ;;
    down|stop)
        echo -e "${BLUE}🛑 停止服务...${NC}"
        $COMPOSE down
        ;;
    rebuild)
        echo -e "${BLUE}🔄 重建镜像并启动...${NC}"
        $COMPOSE down
        $COMPOSE up -d --build
        ;;
    restart)
        echo -e "${BLUE}🔄 重启服务...${NC}"
        $COMPOSE down
        $COMPOSE up -d
        ;;
    logs)
        SERVICE="${2:-web}"
        echo -e "${BLUE}📜 查看 ${SERVICE} 日志 (Ctrl+C 退出)...${NC}"
        $COMPOSE logs -f "$SERVICE"
        ;;
    shell)
        echo -e "${BLUE}🐍 进入 Django Shell...${NC}"
        $COMPOSE exec web python manage.py shell
        ;;
    bash|exec)
        echo -e "${BLUE}💻 进入 Web 容器...${NC}"
        $COMPOSE exec web bash
        ;;
    
    # ✅ 新增：初始化命令（一键完成新环境搭建）
    init|setup)
        echo -e "${BLUE}================================${NC}"
        echo -e "${BLUE}  🚀 初始化新环境 🔧${NC}"
        echo -e "${BLUE}================================${NC}"
        echo
        
        # 1. 确保服务已启动
        echo -e "${YELLOW}📦 步骤 1/3: 检查服务状态...${NC}"
        if ! $COMPOSE ps | grep -q "web.*Up"; then
            echo -e "${YELLOW}⚠️  服务未运行，正在启动...${NC}"
            ./start.sh up
            sleep 5
        else
            echo -e "${GREEN}✅ 服务运行中${NC}"
        fi
        echo
        
        # 2. 执行数据库迁移
        echo -e "${YELLOW}🗄️  步骤 2/3: 执行数据库迁移...${NC}"
        $COMPOSE exec web python manage.py migrate --noinput
        echo -e "${GREEN}✅ 迁移完成${NC}"
        echo
        
        # 3. 收集静态文件（解决样式丢失问题！）
        echo -e "${YELLOW}🎨 步骤 3/3: 收集静态文件 (Admin 样式必备)...${NC}"
        $COMPOSE exec web python manage.py collectstatic --noinput
        echo -e "${GREEN}✅ 静态文件已收集${NC}"
        echo
        
        # 4. 创建管理员账号
        echo -e "${YELLOW}👤 创建管理员账号:${NC}"
        $COMPOSE exec web python manage.py createsuperuser
        
        # 5. 完成提示
        echo
        echo -e "${GREEN}================================${NC}"
        echo -e "${GREEN}  ✨ 初始化完成！${NC}"
        echo -e "${GREEN}================================${NC}"
        echo
        echo -e "  🔐 后台地址: ${GREEN}https://localhost/admin/${NC}"
        echo -e "  👤 用户名: ${GREEN}你刚刚输入的账号${NC}"
        echo -e "  💡 提示: 浏览器点'高级→继续'访问自签证书站点"
        echo
        ;;
    
    migrate)
        echo -e "${BLUE}🗄️ 执行数据库迁移...${NC}"
        $COMPOSE exec web python manage.py migrate
        ;;
    makemigrations)
        echo -e "${BLUE}📝 生成迁移文件...${NC}"
        $COMPOSE exec web python manage.py makemigrations
        ;;
    collectstatic)
        echo -e "${BLUE}🎨 收集静态文件...${NC}"
        $COMPOSE exec web python manage.py collectstatic --noinput
        ;;
    superuser)
        echo -e "${BLUE}👤 创建管理员账号...${NC}"
        $COMPOSE exec web python manage.py createsuperuser
        ;;
    clean)
        echo -e "${RED}🧹 清理容器+数据卷（⚠️ 数据将丢失）...${NC}"
        read -p "确认继续? (y/N): " confirm
        [[ "$confirm" =~ ^[yY] ]] && $COMPOSE down -v || echo "已取消"
        ;;
    cert)
        ensure_cert
        ;;
    ps)
        $COMPOSE ps
        ;;
    help|--help|-h|*)
        echo -e "${BLUE}================================${NC}"
        echo -e "${BLUE}  Django + Docker 开发 CLI 🔧${NC}"
        echo -e "${BLUE}================================${NC}"
        echo
        echo -e "用法: ${GREEN}./start.sh <command>${NC}"
        echo
        echo -e "  ${YELLOW}up / start${NC}       启动所有服务（自动检查 .env 和证书）"
        echo -e "  ${YELLOW}down / stop${NC}      停止服务"
        echo -e "  ${YELLOW}rebuild${NC}          重建镜像并启动"
        echo -e "  ${YELLOW}restart${NC}          重启服务"
        echo -e "  ${YELLOW}init / setup${NC}     ✨ 初始化新环境(迁移+静态文件+管理员)"
        echo -e "  ${YELLOW}logs [service]${NC}   查看日志（默认 web，如 nginx/redis）"
        echo -e "  ${YELLOW}shell${NC}            进入 Django Shell"
        echo -e "  ${YELLOW}bash${NC}             进入 Web 容器终端"
        echo -e "  ${YELLOW}migrate${NC}          执行数据库迁移"
        echo -e "  ${YELLOW}makemigrations${NC}   生成迁移文件"
        echo -e "  ${YELLOW}collectstatic${NC}    收集静态文件(解决样式丢失)"
        echo -e "  ${YELLOW}superuser${NC}        创建管理员账号"
        echo -e "  ${YELLOW}clean${NC}            清理容器+数据卷（二次确认）"
        echo -e "  ${YELLOW}ps${NC}               查看运行状态"
        echo -e "  ${YELLOW}help${NC}             显示此帮助"
        echo
        echo -e "${YELLOW}💡 提示: 所有命令均自动处理环境依赖，无需手动干预${NC}"
        ;;
esac