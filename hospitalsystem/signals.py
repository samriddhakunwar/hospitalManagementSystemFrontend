from django.apps import AppConfig
from django.contrib.auth.models import User
from django.db.models.signals import post_migrate
from django.dispatch import receiver

class YourAppConfig(AppConfig):
    name = 'hospitalsystem'

    def ready(self):
        post_migrate.connect(create_default_admin)

@receiver(post_migrate)
def create_default_admin(sender, **kwargs):
    username = 'admin'
    email = 'admin@example.com'
    password = 'adminpassword'  
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f'Superuser "{username}" created successfully.')
    else:
        print(f'Superuser "{username}" already exists.')
