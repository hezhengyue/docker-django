# config/settings.py

import os
import sys
import re
from pathlib import Path
from datetime import timedelta
from django.core.exceptions import ImproperlyConfigured
import environ
from urllib.parse import quote_plus



# 📂 项目根目录：config/settings.py 所在目录的父级
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_NAME = BASE_DIR.name

# 📦 环境变量初始化：
env = environ.Env()
# 🔍 加载环境变量：优先级 .env.local > .env > 默认值。支持本地覆盖不提交
environ.Env.read_env(BASE_DIR.parent / '.env')


# 📌 读取核心配置：无默认值变量必须存在，否则启动报错
SECRET_KEY = env('SECRET_KEY', default='')
DEBUG = env.bool('DEBUG', default=False)


# ===================== 🌐 访问与安全 =====================
# ===================== 🌐 访问与安全 =====================

HOSTS = list({
    'localhost',
    '127.0.0.1',
    *env.list('HOSTS', default=[]),
})
# 谁可以访问 Django
ALLOWED_HOSTS = HOSTS.copy()
# 自动生成 CSRF Trusted Origins
schemes = ['http', 'https'] if DEBUG else ['https']
CSRF_TRUSTED_ORIGINS = [
    f'{scheme}://{host}'
    for host in HOSTS
    for scheme in schemes
]
# 谁有资格告诉 Django：“真实客户端 IP 是谁”，因为使用docker，网络层已经隔离，无需配置
TRUSTED_PROXIES = []


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
    'common.apps.CommonConfig',
    'jobs',
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
    "common.middleware.real_ip.RealIPMiddleware" # 判断真实ip
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


# ===================== 🌏 国际化 =====================
# 默认语言：zh-hans(简体中文)/en-us(英文)。影响后台与模板翻译
LANGUAGE_CODE="zh-hans"
# 默认时区：Asia/Shanghai(中国)/UTC(国际)。影响 now() 与数据库存储
TIME_ZONE="Asia/Shanghai"
USE_I18N = True
# 启用时区支持：True=存UTC显本地(推荐)/False=存本地(易混乱)
USE_TZ= True


# 标准判断：容器内存在 /.dockerenv 文件, 自动识别 本地/容器
IN_DOCKER = os.path.exists("/.dockerenv")


# 🗄️ 数据库配置：直接使用 POSTGRES_* 变量拼接，无需 DATABASE_URL
POSTGRES_HOST ="localhost"
if IN_DOCKER:
    POSTGRES_HOST = "db"
POSTGRES_PORT = 5432
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
REDIS_HOST = "localhost"
if IN_DOCKER:
    REDIS_HOST = "redis"
REDIS_PORT = 6379
REDIS_PASSWORD = env('REDIS_PASSWORD', default='Redis1234')
REDIS_DB = 0
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
CELERY_BROKER_DB = 1
CELERY_RESULT_BACKEND_DB = 2
CELERY_BROKER_URL = f"redis://{_redis_auth}{REDIS_HOST}:{REDIS_PORT}/{CELERY_BROKER_DB}"
CELERY_RESULT_BACKEND = f"redis://{_redis_auth}{REDIS_HOST}:{REDIS_PORT}/{CELERY_RESULT_BACKEND_DB}"
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TIME_LIMIT = 300




# 🔐 密码校验器：防弱密码/与用户名相似/常见字典密码
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ===================== 🔑 会话配置 =====================
# 🔑 会话引擎：cached_db 兼顾性能与持久化。Cookie 安全标志按 .env 动态切换
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
SESSION_COOKIE_AGE=1200
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
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


# ===================== 📁 文件上传 =====================
# 请求体最大内存缓冲：超过则落盘。必须 ≤ Nginx client_max_body_size
DATA_UPLOAD_MAX_MEMORY_SIZE=50 * 1024 * 1024
# 单文件最大内存缓冲：同上，针对单个文件。按业务调整(头像 2M/视频 500M)
FILE_UPLOAD_MAX_MEMORY_SIZE=50 * 1024 * 1024


# ===================== 📝 日志配置 =====================
# 📝 日志配置：开发彩色控制台 + 生产 JSON + 按天轮转文件。保留天数从 .env 读取
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_LEVEL = "DEBUG" if DEBUG else "INFO"
LOG_FILE_LEVEL = "INFO" if DEBUG else "WARNING"
LOG_RETENTION_DAYS=90

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



# email 配置：使用 SMTP 后端，参数从 .env 读取。生产环境务必设置 EMAIL_HOST_PASSWORD（授权码）
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT', default=25) 
# 🔹 读取协议（统一小写 + 校验）
EMAIL_PROTOCOL = env.str('EMAIL_PROTOCOL', default='ssl').strip().lower()
VALID_PROTOCOLS = {'ssl', 'tls', 'none'}
if EMAIL_PROTOCOL not in VALID_PROTOCOLS:
    raise ValueError(f"EMAIL_PROTOCOL 必须是 {VALID_PROTOCOLS} 之一，当前值: '{EMAIL_PROTOCOL}'")
# 🔹 自动转换为 Django 需要的布尔配置
EMAIL_USE_SSL = (EMAIL_PROTOCOL == 'ssl')
EMAIL_USE_TLS = (EMAIL_PROTOCOL == 'tls')
# none 时两者都为 False，使用明文 SMTP（仅内网测试）
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD') 
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# django-axes配置
INSTALLED_APPS += [
    'axes',
]
# 插入到 AuthenticationMiddleware 后面
auth_index = MIDDLEWARE.index('django.contrib.auth.middleware.AuthenticationMiddleware')

MIDDLEWARE.insert(auth_index + 1, 'axes.middleware.AxesMiddleware')
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]
# 登录失败限制
AXES_FAILURE_LIMIT = 5
# 封禁时间
AXES_COOLOFF_TIME = timedelta(hours=1)
# 同一个ip只锁定一个账户
AXES_LOCKOUT_PARAMETERS = [["ip_address", "username"]]
# 登录成功自动重置
AXES_RESET_ON_SUCCESS = True
# Admin 后台
AXES_ENABLE_ADMIN = True
# 返回403
AXES_HTTP_RESPONSE_CODE = 403
# 使用 Redis 缓存
AXES_CACHE = 'default'


# django_celery_beat配置
INSTALLED_APPS += [
    'django_celery_beat',
]


# django-import-export配置
INSTALLED_APPS += [
    'import_export',
]
IMPORT_EXPORT_USE_TRANSACTIONS = True
IMPORT_EXPORT_SKIP_ADMIN_CONFIRM = False


# django-auditlog配置
INSTALLED_APPS +=  [
    'auditlog',
]
MIDDLEWARE += [
    'auditlog.middleware.AuditlogMiddleware',
]

# ===================== SimpleUI后台美化配置 =====================
INSTALLED_APPS = [
    'simpleui',
] + INSTALLED_APPS

SIMPLEUI_HOME_INFO = False
SIMPLEUI_ANALYSIS = False
SIMPLEUI_STATIC_OFFLINE = True

logo_file_path = MEDIA_ROOT / 'logo.png'
if logo_file_path.exists():
    SIMPLEUI_LOGO = '/media/logo.png'

# 定义图标 (common.admin.rename.py对第三方插件重命名)
SIMPLEUI_ICON = {
    '用户管理': 'far fa-bars',
    '人员档案': 'far fa-person',

    '任务中心': 'far fa-bars',
    
    '安全监控': 'fas fa-shield-alt',     
    '锁定记录': 'fas fa-lock',           
    '登录流水': 'fas fa-list-alt',      
    
    '操作审计': 'fas fa-history',        
    '操作日志': 'fas fa-file-signature',  
}

# SimpleUI自定义菜单配置
SIMPLEUI_CONFIG = {
    'system_keep': False,
    'menu_display': [
        '用户管理',       # core
        '任务中心',       # jobs
        '安全监控',       # Axes
        '操作审计',       # Audit log
        #'认证和授权',    # 分组
        '定时任务',       # django_celery_beat
    ], 
    'dynamic': True,
    # 自定义菜单
    # 'menus': [
    #     {
    #         'name': '人脸识别',
    #         'icon': 'far fa-camera',
    #         'models': [
    #             {
    #                 'name': '开始识别',
    #                 'url': '/face-scan/',
    #                 'icon': 'fas fa-search'
    #             }
    #         ]
    #     },
    # ]
}



# 🛡️ 生产环境安全拦截（放在文件末尾，DEBUG 判断之后）
if not DEBUG:
    if not SECRET_KEY or SECRET_KEY.startswith('django-insecure'):
        raise ImproperlyConfigured("生产环境 SECRET_KEY 必须更换且不能为空！")
    
    if '*' in ALLOWED_HOSTS:
        raise ImproperlyConfigured("生产环境 ALLOWED_HOSTS 禁止使用 * ！")
    
    # 可选：检查 CSRF_TRUSTED_ORIGINS 是否包含 https（生产建议）
    if not any(origin.startswith('https://') for origin in CSRF_TRUSTED_ORIGINS):
        import warnings
        warnings.warn(
            "生产环境建议 CSRF_TRUSTED_ORIGINS 配置 https:// 开头的域名",
            RuntimeWarning
        )

