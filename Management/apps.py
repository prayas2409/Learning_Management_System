from django.apps import AppConfig


class ManagementConfig(AppConfig):
    name = 'Management'

    def ready(self):
        import Management.signals
