from django.apps import AppConfig


class SandboxConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sandbox'

    def ready(self):
        import sandbox.signals  # noqa
