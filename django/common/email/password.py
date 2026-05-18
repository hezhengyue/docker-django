# common/email/password.py
import secrets
from .tasks import send_password_email_task  # 🔁 导入 Celery 任务

def generate_secure_password(length=10):
    """生成含大小写字母+数字的随机密码"""
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    while True:
        pwd = ''.join(secrets.choice(chars) for _ in range(length))
        if (any(c.isupper() for c in pwd) and 
            any(c.islower() for c in pwd) and 
            any(c.isdigit() for c in pwd)):
            return pwd

def send_temp_password_email(user_email: str, password: str, username: str = ''):
    """
    发送临时密码邮件（异步非阻塞）
    返回: task_id (str) 或 None（如果邮箱为空）
    """
    if not user_email:
        return None
    
    # 🔁 异步投递任务，立即返回 task_id
    task = send_password_email_task.delay(
        user_email=user_email,
        password=password,
        username=username
    )
    return task.id