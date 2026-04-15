FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /app

# 🔧 1. 系统依赖安装（🔑 必须在 USER 之前，此时是 root 用户）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl git \
    && rm -rf /var/lib/apt/lists/*

# 🔧 2. pip 配置（🔑 必须在 USER 之前）
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/

# 🔑 3. 依赖安装（🔑 必须在 USER 之前，且放在代码复制前以利用缓存）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 🔑 4. 复制代码
COPY . .

# 🔐 5. 创建非 root 用户 + 预创建目录 + 授权（🔑 必须在 USER 之前，用 root 执行）
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/logs /app/staticfiles /app/media && \
    chown -R appuser:appuser /app

# 🔑 6. 最后切换用户（所有特权操作完成后）
USER appuser

EXPOSE 8000

# 🎯 默认命令
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]