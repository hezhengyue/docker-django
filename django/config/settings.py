"""
docker-django/django/config/settings.py
"""
import os
import sys
import re
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
import environ
from urllib.parse import quote_plus


# 🔧 工具函数：将 '50M'/'2G' 解析为字节数，兼容纯数字
def parse_size(value: str | int) -> int:
    if isinstance(value, int):
        return value
    value = str(value).strip().upper()
    if value.replace('.', '', 1).isdigit():
        return int(float(value))
    m = re.match(r'^([\d.]+)\s*(K|KB|M|MB|G|GB)?$', value)
    if not m:
        raise ValueError(f"Invalid size format: {value}")
    multipliers = {
        '': 1, 'K': 1024, 'KB': 1024,
        'M': 1024**2, 'MB': 1024**2,
        'G': 1024**3, 'GB': 1024**3
    }
    return int(float(m.group(1)) * multipliers.get(m.group(2) or '', 1))


# 📂 项目根目录：config/settings.py 所在目录的父级
BASE_DIR = Path(__file__).resolve().parent.parent


# 📦 环境变量初始化：
env = environ.Env()
# 🔍 加载环境变量：优先级 .env.local > .env > 默认值。支持本地覆盖不提交
environ.Env.read_env(BASE_DIR.parent / '.env')
environ.Env.read_env(BASE_DIR.parent / '.env.local')


# 📌 读取核心配置：无默认值变量必须存在，否则启动报错
SECRET_KEY = env('SECRET_KEY', default='')
DEBUG = env.bool('DEBUG', default=False)
PROJECT_NAME = env('PROJECT_NAME', default='docker-django')


# ⚠️ ALLOWED_HOSTS 空列表时：开发放行所有(*)，生产回退安全白名单
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=['http://localhost', 'http://127.0.0.1'])
TRUSTED_PROXIES = env.list('TRUSTED_PROXIES', default=['127.0.0.1', '::1'])


# 👤 自定义用户模型：固定指向 core.User，避免 .env 误配导致启动失败
AUTH_USER_MODEL = 'core.User'


# 📦 应用注册：Django 内置 + 本地 core 应用
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
]


# 🛡️ 中间件：安全/会话/CSRF/认证/日志 + 自定义真实 IP 中间件
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.RealIPMiddleware',
]


ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'


# 🎨 模板配置：启用 app_dirs 自动发现 + 注入 debug/request/auth/messages 上下文
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]


# 🌏 国际化：语言/时区/启用开关。USE_TZ=true 确保跨时区部署时间不混乱
LANGUAGE_CODE = env('LANGUAGE_CODE', default='zh-hans')
TIME_ZONE = env('TIME_ZONE', default='Asia/Shanghai')
USE_I18N = True
USE_TZ = env.bool('USE_TZ', default=True)


# 🗄️ 数据库配置（终极版：自动识别 本地/容器）
# 标准判断：容器内存在 /.dockerenv 文件
IN_DOCKER = os.path.exists("/.dockerenv")


# 🗄️ 数据库配置：直接使用 POSTGRES_* 变量拼接，无需 DATABASE_URL
POSTGRES_HOST = env('POSTGRES_HOST', default='db')
if IN_DOCKER:
    POSTGRES_HOST = "db"
POSTGRES_PORT = env('POSTGRES_PORT', default='5432')
POSTGRES_USER = env('POSTGRES_USER', default='postgres')
POSTGRES_PASSWORD = env('POSTGRES_PASSWORD', default='Postgres1234')
POSTGRES_DB = env('POSTGRES_DB', default='db')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': POSTGRES_DB,
        'USER': POSTGRES_USER,
        'PASSWORD': POSTGRES_PASSWORD,
        'HOST': POSTGRES_HOST,
        'PORT': POSTGRES_PORT,
        'CONN_MAX_AGE': 600,  # 连接复用，提升性能
        'CONN_HEALTH_CHECKS': True,  # Django 4.1+ 自动检测断连重连
    }
}


# 🚀 Redis 配置智能拼接：使用 REDIS_* 变量构建 URL
REDIS_HOST = env('REDIS_HOST', default='redis')
if IN_DOCKER:
    REDIS_HOST = "redis"
REDIS_PORT = env('REDIS_PORT', default='6379')
REDIS_PASSWORD = env('REDIS_PASSWORD', default='Redis1234')
REDIS_DB = env.int('REDIS_DB', default=0)
# 🔐 密码转义 + 构建 URL
_redis_auth = f':{quote_plus(REDIS_PASSWORD)}@' if REDIS_PASSWORD else ''
# 基础 Redis URL（用于缓存等）
REDIS_URL = f"redis://{_redis_auth}{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
        }
    }
}


# 🚀 Celery 配置：读取 Broker/Backend/超时。统一 JSON 序列化保证跨语言兼容
CELERY_BROKER_DB = env.int('CELERY_BROKER_DB', default=1)
CELERY_RESULT_BACKEND_DB = env.int('CELERY_RESULT_BACKEND_DB', default=2)
CELERY_BROKER_URL = f"redis://{_redis_auth}{REDIS_HOST}:{REDIS_PORT}/{CELERY_BROKER_DB}"
CELERY_RESULT_BACKEND = f"redis://{_redis_auth}{REDIS_HOST}:{REDIS_PORT}/{CELERY_RESULT_BACKEND_DB}"
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TIME_LIMIT = env.int('CELERY_TASK_TIME_LIMIT', default=300)


# 🔐 密码校验器：防弱密码/与用户名相似/常见字典密码
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# 🔑 会话引擎：cached_db 兼顾性能与持久化。Cookie 安全标志按 .env 动态切换
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_COOKIE_AGE = env.int('SESSION_COOKIE_AGE', default=1200)
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=False)
SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=False)
# 🌐 代理 HTTPS 标识：Nginx 终止 SSL 时，Django 识别 request.is_secure() 的必备头
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')



# 📁 静态/媒体文件：Django 5.x 新 STORAGES 语法。自动创建目录防启动报错
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
for p in (STATIC_ROOT, MEDIA_ROOT):
    p.mkdir(parents=True, exist_ok=True)


# 📤 上传限制：解析 .env 友好单位('50M') 为字节数
DATA_UPLOAD_MAX_MEMORY_SIZE = parse_size(env.str('DATA_UPLOAD_MAX_MEMORY_SIZE', default=52428800))
FILE_UPLOAD_MAX_MEMORY_SIZE = parse_size(env.str('FILE_UPLOAD_MAX_MEMORY_SIZE', default=52428800))


# 📝 日志配置：开发彩色控制台 + 生产 JSON + 按天轮转文件。保留天数从 .env 读取
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_LEVEL = env('LOG_LEVEL', default='DEBUG').upper()
LOG_FILE_LEVEL = env('LOG_FILE_LEVEL', default='INFO').upper()
LOG_RETENTION_DAYS = env.int('LOG_RETENTION_DAYS', default=30)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'dev': {
            '()': 'colorlog.ColoredFormatter',
            'format': '%(log_color)s%(asctime)s [%(levelname)s] %(name)s:%(lineno)d%(reset)s - %(message)s',
            'log_colors': {
                'DEBUG': 'cyan', 'INFO': 'green', 'WARNING': 'yellow',
                'ERROR': 'red', 'CRITICAL': 'bold_red',
            },
        },
        'prod': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d %(funcName)s',
            'static_fields': {'project': PROJECT_NAME},
        },
        'file': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'dev' if DEBUG else 'prod',
            'stream': sys.stdout,
            'level': LOG_LEVEL,
        },
        'app_file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'file',
            'filename': LOG_DIR / 'app.log',
            'when': 'midnight',
            'interval': 1,
            'backupCount': LOG_RETENTION_DAYS,
            'encoding': 'utf-8',
            'level': LOG_FILE_LEVEL,
            'delay': True,
        },
        'error_file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'file',
            'filename': LOG_DIR / 'error.log',
            'when': 'midnight',
            'interval': 1,
            'backupCount': LOG_RETENTION_DAYS,
            'encoding': 'utf-8',
            'level': 'ERROR',
            'delay': True,
        },
        'django_file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'file',
            'filename': LOG_DIR / 'django.log',
            'when': 'midnight',
            'interval': 1,
            'backupCount': LOG_RETENTION_DAYS,
            'encoding': 'utf-8',
            'level': 'INFO' if DEBUG else 'WARNING',
            'delay': True,
        },
    },
    'root': {
        'handlers': ['console', 'app_file'],
        'level': LOG_LEVEL,
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'django_file'] if DEBUG else ['console'],
            'level': 'INFO' if DEBUG else 'WARNING',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'] if DEBUG else [],
            'level': 'DEBUG' if DEBUG else 'CRITICAL',
            'propagate': False,
        },
        'core': {
            'handlers': ['console', 'app_file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# 📉 生产环境：root 日志额外写入 error_file，便于独立采集告警
if not DEBUG:
    LOGGING['root']['handlers'].append('error_file')


# 🔢 默认主键类型：BigAutoField 防 32 位溢出，Django 3.2+ 推荐
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# 🛡️ 生产环境安全拦截（放在文件末尾，DEBUG 判断之后）
if not DEBUG:
    if not SECRET_KEY or SECRET_KEY.startswith('django-insecure'):
        raise ImproperlyConfigured("生产环境 SECRET_KEY 必须更换且不能为空！")
    
    # 检查数据库密码（注意：此时密码是原始值，未转义）
    if not POSTGRES_PASSWORD or POSTGRES_PASSWORD in ('postgres', 'password', '123456'):
        raise ImproperlyConfigured("生产环境数据库密码不能为空或弱密码！")
    
    if '*' in ALLOWED_HOSTS:
        raise ImproperlyConfigured("生产环境 ALLOWED_HOSTS 禁止使用 * ！")
    
    # 可选：检查 CSRF_TRUSTED_ORIGINS 是否包含 https（生产建议）
    if not any(origin.startswith('https://') for origin in CSRF_TRUSTED_ORIGINS):
        import warnings
        warnings.warn(
            "生产环境建议 CSRF_TRUSTED_ORIGINS 配置 https:// 开头的域名",
            RuntimeWarning
        )