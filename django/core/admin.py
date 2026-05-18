# core/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User

from import_export.admin import ImportExportModelAdmin
from .resources import UserResource

admin.site.site_header = _('后台管理')
admin.site.site_title = _('后台管理')
admin.site.index_title = _('控制台')

# ✅ 继承顺序：ImportExportModelAdmin 在前，保留其导入导出功能
@admin.register(User)
class UserAdmin(ImportExportModelAdmin, BaseUserAdmin):
    resource_classes = [UserResource]  # ⚠️ v3+ 必须为列表
    
    list_display = ('username', 'email', 'phone', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'date_joined')
    search_fields = ('username', 'email', 'phone', 'first_name', 'last_name')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('last_login', 'date_joined')
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['phone'].required = False
        return form



# =========================================================
# auditlog显示IP
# =========================================================
from auditlog.models import LogEntry
from auditlog.admin import LogEntryAdmin

# 1. 先取消 auditlog 默认的注册
if admin.site.is_registered(LogEntry):
    admin.site.unregister(LogEntry)

# 2. 定义新的 Admin 类
@admin.register(LogEntry)
class CustomLogEntryAdmin(LogEntryAdmin):
    
    list_display = [
    # 核心必显字段（优先级从高到低）
    'timestamp',       # 1. 操作时间（最核心，排查问题先看时间）
    'user_url',        # 2. 操作用户（谁做的）
    'remote_addr',     # 3. IP地址（从哪来的）
    'action',          # 4. 操作类型（增/删/改）
    'resource_url',    # 5. 操作资源（改了哪个对象）
    'msg_short',       # 6. 操作内容（改了什么）
]

    # 搜索和筛选保持实用即可
    search_fields = ['timestamp', 'actor__username', 'remote_addr', 'object_repr', 'changes']
    list_filter = ['action', 'timestamp', 'actor', 'remote_addr']  
    readonly_fields = [field.name for field in LogEntry._meta.fields]
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'
    list_per_page = 50
    # 禁止修改审计日志
    def has_change_permission(self, request, obj=None):
        return False
    # 禁止删除审计日志
    def has_delete_permission(self, request, obj=None):
        return False
    # 禁止新增审计日志
    def has_add_permission(self, request):
        return False