from django.apps import AppConfig


class NewsappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'newsapp'

    def ready(self) -> None:

        print("NewsappConfig.ready() called!")
        import newsapp.signals
