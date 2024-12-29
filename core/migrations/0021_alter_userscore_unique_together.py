# Generated by Django 5.1.4 on 2024-12-29 01:02

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0020_alter_userscore_user"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="userscore",
            unique_together={("user", "date")},
        ),
    ]
