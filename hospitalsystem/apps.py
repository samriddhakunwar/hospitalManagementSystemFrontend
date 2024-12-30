from django.apps import AppConfig

class HospitalsystemConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hospitalsystem'

    def ready(self):
        import hospitalsystem.signals