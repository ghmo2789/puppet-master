from django.apps import AppConfig


class WebsiteConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "website"

class NotisConfig(AppConfig):
    name = "website"

    def ready(self):
        try:
            import website.signals 
        except ImportError:
            print('IMPORT ERROR!!!!!!!!!')
            pass
