"""
docker-django/django/core/utils.py - Django 项目核心工具函数
"""
def get_client_ip(request):
    """获取客户端真实 IP"""
    if hasattr(request, '_real_ip'):
        return request._real_ip
    return request.META.get('REMOTE_ADDR', '0.0.0.0')

def format_phone(phone: str) -> str:
    """格式化手机号：13800138000 → 138****8000"""
    if not phone or len(str(phone)) != 11:
        return str(phone)
    return f"{str(phone)[:3]}****{str(phone)[-4:]}"

def safe_int(value, default=0):
    """安全转换整数"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default