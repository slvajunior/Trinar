# Generated by Django 5.1.3 on 2024-12-04 05:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0002_alter_notification_notifications_type_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="notification",
            old_name="notifications_type",
            new_name="notification_type",
        ),
    ]
