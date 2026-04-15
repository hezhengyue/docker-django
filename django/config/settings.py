"""Django 核心配置 - 所有业务参数从 .env 读取，保留安全默认值"""
import os
import sys
import re
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
import environ


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


# 📦 环境变量初始化：声明所有支持的变量、类型、安全兜底默认值
env = environ.Env(
    # 🔐 核心安全 (用户必配)
    SECRET_KEY=(str, ''),
    DEBUG=(bool, False),
    PROJECT_NAME=(str, 'docker-django'),

    # 🌐 访问控制 (用户必配)
    ALLOWED_HOSTS=(list, []),
    CSRF_TRUSTED_ORIGINS=(list, []),
    TRUSTED_PROXIES=(list, ['127.0.0.1', '::1']),

    # 🔑 会话配置 (按需调整)
    SESSION_COOKIE_AGE=(int, 1200),
    CSRF_COOKIE_SECURE=(bool, False),
    SESSION_COOKIE_SECURE=(bool, False),

    # 🗄️ 数据库配置 (自动拼接)
    DATABASE_URL=(str, ''),
    POSTGRES_HOST=(str, 'db'),
    POSTGRES_PORT=(str, '5432'),

    # 🚀 异步任务 (Celery)
    CELERY_BROKER_URL=(str, 'redis://redis:6379/0'),
    CELERY_RESULT_BACKEND=(str, 'redis://redis:6379/0'),
    CELERY_TASK_TIME_LIMIT=(int, 300),

    # 📝 日志配置
    LOG_LEVEL=(str, 'DEBUG'),
    LOG_FILE_LEVEL=(str, 'INFO'),
    LOG_RETENTION_DAYS=(int, 30),

    # 📁 文件上传限制
    DATA_UPLOAD_MAX_MEMORY_SIZE=(str, '50M'),
    FILE_UPLOAD_MAX_MEMORY_SIZE=(str, '50M'),

    # 🌏 国际化配置
    LANGUAGE_CODE=(str, 'zh-hans'),
    TIME_ZONE=(str, 'Asia/Shanghai'),
    USE_TZ=(bool, True),
)

# 🔍 加载环境变量：优先级 .env.local > .env > 默认值。支持本地覆盖不提交
environ.Env.read_env(BASE_DIR.parent / '.env')
environ.Env.read_env(BASE_DIR.parent / '.env.local')


# 📌 读取核心配置：无默认值变量必须存在，否则启动报错
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
PROJECT_NAME = env('PROJECT_NAME')

# ⚠️ ALLOWED_HOSTS 空列表时：开发放行所有(*)，生产回退安全白名单
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS') or (['*'] if DEBUG else ['localhost', '127.0.0.1'])
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS')
TRUSTED_PROXIES = env.list('TRUSTED_PROXIES')

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


# 🗄️ 数据库智能拼接：优先读 DATABASE_URL(.env) → 缺失则用 POSTGRES_* 拼 → 兜底安全报错
_db = env('DATABASE_URL', default='')
if not _db:
    _db = (
        f"postgresql://"
        f"{os.getenv('POSTGRES_USER', 'postgres')}:"
        f"{os.getenv('POSTGRES_PASSWORD', 'postgres')}@"
        f"{os.getenv('POSTGRES_HOST', 'db')}:"
        f"{os.getenv('POSTGRES_PORT', '5432')}/"
        f"{os.getenv('POSTGRES_DB', 'db')}"
    )
DATABASES = {'default': env.db_url('DATABASE_URL', default=_db)}


# 🔐 密码校验器：防弱密码/与用户名相似/常见字典密码
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# 🔑 会话引擎：cached_db 兼顾性能与持久化。Cookie 安全标志按 .env 动态切换
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_COOKIE_AGE = env('SESSION_COOKIE_AGE')
CSRF_COOKIE_SECURE = env('CSRF_COOKIE_SECURE')
SESSION_COOKIE_SECURE = env('SESSION_COOKIE_SECURE')

# 🌐 代理 HTTPS 标识：Nginx 终止 SSL 时，Django 识别 request.is_secure() 的必备头
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# 🌏 国际化：语言/时区/启用开关。USE_TZ=true 确保跨时区部署时间不混乱
LANGUAGE_CODE = env('LANGUAGE_CODE')
TIME_ZONE = env('TIME_ZONE')
USE_I18N = True
USE_TZ = env('USE_TZ')


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
DATA_UPLOAD_MAX_MEMORY_SIZE = parse_size(env('DATA_UPLOAD_MAX_MEMORY_SIZE'))
FILE_UPLOAD_MAX_MEMORY_SIZE = parse_size(env('FILE_UPLOAD_MAX_MEMORY_SIZE'))


# 🚀 Celery 配置：读取 Broker/Backend/超时。统一 JSON 序列化保证跨语言兼容
CELERY_BROKER_URL = env('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TIME_LIMIT = env('CELERY_TASK_TIME_LIMIT')


# 📝 日志配置：开发彩色控制台 + 生产 JSON + 按天轮转文件。保留天数从 .env 读取
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)

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
            'level': env('LOG_LEVEL'),
        },
        'app_file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'file',
            'filename': LOG_DIR / 'app.log',
            'when': 'midnight',
            'interval': 1,
            'backupCount': env('LOG_RETENTION_DAYS'),
            'encoding': 'utf-8',
            'level': env('LOG_FILE_LEVEL'),
            'delay': True,
        },
        'error_file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'file',
            'filename': LOG_DIR / 'error.log',
            'when': 'midnight',
            'interval': 1,
            'backupCount': env('LOG_RETENTION_DAYS'),
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
            'backupCount': env('LOG_RETENTION_DAYS'),
            'encoding': 'utf-8',
            'level': 'INFO' if DEBUG else 'WARNING',
            'delay': True,
        },
    },
    'root': {
        'handlers': ['console', 'app_file'],
        'level': env('LOG_LEVEL'),
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


# 🛡️ 生产安全拦截：DEBUG=false 时强制检查密钥/密码/Host，防止危险配置上线
if not DEBUG:
    if SECRET_KEY.startswith('django-insecure'):
        raise ImproperlyConfigured("生产环境 SECRET_KEY 必须更换！")
    if DATABASES['default'].get('PASSWORD') in ('', 'postgres', None):
        raise ImproperlyConfigured("生产环境数据库密码不能为空或默认值！")
    if '*' in ALLOWED_HOSTS:
        raise ImproperlyConfigured("生产环境 ALLOWED_HOSTS 禁止使用 *！")