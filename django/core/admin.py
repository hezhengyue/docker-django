from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password, identify_hasher

from .models import User


# =========================
# 🔥 后台标题
# =========================
admin.site.site_header = _('后台管理')
admin.site.site_title = _('后台管理')
admin.site.index_title = _('控制台')



# =========================
# 🧠 Admin 主体
# =========================
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # =========================
    # 📋 列表页
    # =========================
    list_display = ('username', 'email', 'phone', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'date_joined')
    search_fields = ('username', 'email', 'phone', 'first_name', 'last_name')
    ordering = ('username',)

    # =========================
    # 🧾 表单结构
    # =========================
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone', 'password1', 'password2'),
        }),
    )

    readonly_fields = ('last_login', 'date_joined')

    # =========================
    # 🧩 form 安全处理
    # =========================
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        if 'phone' in form.base_fields:
            form.base_fields['phone'].required = False

        return form