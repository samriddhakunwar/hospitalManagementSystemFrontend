# Generated by Django 5.1.1 on 2024-10-01 05:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospitalsystem', '0004_appointment_emergency'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='is_emergency',
            field=models.BooleanField(default=False),
        ),
    ]
