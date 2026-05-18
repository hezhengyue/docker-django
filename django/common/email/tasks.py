# common/email/tasks.py
import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

@shared_task(bind=True)  # 🔹 移除 max_retries、default_retry_delay
def send_password_email_task(self, user_email: str, password: str, username: str = ''):
    """
    异步发送临时密码邮件（单次执行，无重试）
    """
    subject = '【系统通知】您的初始密码已生成'
    message = f'您好 {username or "用户"}，\n\n您的临时登录密码为：{password}\n\n为保障安全，请在首次登录后立即修改密码。'
    html_message = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px;">
        <h2>您好 {username or "用户"}，</h2>
        <p>您的临时登录密码已生成：</p>
        <div style="background: #f4f4f4; padding: 15px; font-size: 24px; font-weight: bold; letter-spacing: 2px; border-radius: 5px; text-align: center;">
            {password}
        </div>
        <p style="color: #666; font-size: 14px; margin-top: 20px;">
            ⚠️ 为保障账户安全，请在首次登录后立即修改密码。<br>
            如非本人操作，请忽略此邮件或联系客服。
        </p>
    </div>
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False
        )
        logger.info(f"✅ 异步邮件发送成功: {user_email}")
        return True
        
    except Exception as e:
        # 🔹 关键改动：失败只记录日志，不重试
        logger.error(f"❌ 邮件发送失败 {user_email}: {e}", exc_info=True)
        return False  # 返回 False 表示失败，但不再重试