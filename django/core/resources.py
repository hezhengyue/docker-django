# core/resources.py

from import_export import resources, fields
from import_export.widgets import BooleanWidget

from django.contrib.auth.hashers import make_password, identify_hasher
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import User


class UserResource(resources.ModelResource):
    """
    用户导入导出 Resource

    功能：
    - Excel / CSV 导入导出
    - 自动密码加密
    - Django 强密码校验
    - username 存在则更新
    - password 为空则不修改密码
    - 自动跳过空行
    - 不导出 password hash
    """

    is_active = fields.Field(
        column_name='is_active',
        attribute='is_active',
        widget=BooleanWidget()
    )

    is_staff = fields.Field(
        column_name='is_staff',
        attribute='is_staff',
        widget=BooleanWidget()
    )

    class Meta:
        model = User

        # 允许导入导出的字段
        fields = (
            'username',
            'email',
            'phone',
            'password',
            'is_active',
            'is_staff',
        )

        # 导出字段顺序
        export_order = (
            'username',
            'email',
            'phone',
            'password',
            'is_active',
            'is_staff',
        )

        # 使用 username 作为更新依据
        import_id_fields = ('username',)

        # 跳过未变化数据
        skip_unchanged = True

        # 显示跳过报告
        report_skipped = True

        # 使用事务
        use_transactions = True

    def before_import_row(self, row, **kwargs):
        """
        导入前处理每一行
        """

        # =====================================
        # 空行自动跳过
        # =====================================
        is_empty = all(
            not str(value).strip()
            for value in row.values()
        )

        if is_empty:
            raise resources.SkipRow()

        # =====================================
        # username
        # =====================================
        username = str(row.get('username') or '').strip()

        if not username:
            raise ValidationError('username 不能为空')

        row['username'] = username

        # =====================================
        # email
        # =====================================
        email = str(row.get('email') or '').strip().lower()

        row['email'] = email

        # =====================================
        # phone
        # =====================================
        phone = str(row.get('phone') or '').strip()

        row['phone'] = phone

        # =====================================
        # password
        # =====================================
        password = row.get('password')

        # password 为空 -> 不修改密码
        if password in [None, '']:
            row.pop('password', None)
            return

        password = str(password).strip()

        # 临时用户对象
        temp_user = User(
            username=username,
            email=email,
        )

        try:
            # 已经是 hash
            identify_hasher(password)

        except Exception:

            # Django 强密码验证
            validate_password(password, user=temp_user)

            # hash 密码
            row['password'] = make_password(password)

    def before_save_instance(self, instance, row, **kwargs):
        """
        保存前处理
        """

        # email 小写
        if instance.email:
            instance.email = str(instance.email).lower().strip()

        # phone 去空格
        if instance.phone:
            instance.phone = str(instance.phone).strip()

    def dehydrate_password(self, user):
        """
        导出 password 字段

        企业级：
        不导出真实 hash
        """

        return ''

    def get_instance(self, instance_loader, row):
        """
        username 存在 -> 更新
        username 不存在 -> 创建
        """

        username = str(row.get('username') or '').strip()

        if not username:
            return None

        try:
            return User.objects.get(username=username)

        except User.DoesNotExist:
            return None