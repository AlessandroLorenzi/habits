# Generated by Django 5.1.4 on 2024-12-30 20:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0022_alter_userscore_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="userscore",
            name="accomplished_habits",
            field=models.ManyToManyField(to="core.habit"),
        ),
    ]