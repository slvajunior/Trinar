from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from users.models import Post


class Notification(models.Model):
    user = models.ForeignKey(
        User, related_name="notifications", on_delete=models.CASCADE
    )
    post = models.ForeignKey(
        Post, related_name="notifications", on_delete=models.CASCADE
    )
    notifications_type = models.CharField(max_length=20)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Notificação de {self.notifications_type} para {self.user.username}"
