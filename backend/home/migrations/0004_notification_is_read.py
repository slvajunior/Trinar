# Generated by Django 5.1.3 on 2024-12-08 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0003_notification_repost_user_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="is_read",
            field=models.BooleanField(default=False),
        ),
    ]
