from django.apps import AppConfig


class MesConfig(AppConfig):
    name = 'mes'

    def ready(self) -> None:
        """应用就绪时导入信号处理器."""
        import mes.signals  # noqa: F401
