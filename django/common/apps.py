from django.apps import AppConfig


class CommonConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'common'

    verbose_name = '公共模块'

    def ready(self):

        from .admin.rename import rename_third_party_apps

        rename_third_party_apps()