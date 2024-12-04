from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from users.models import Post
# from .utils import time_diff_in_words


class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ("like", "Like"),
        ("comment", "Comment"),
        ("mention", "Mention"),
        # outros tipos...
    ]
    notification_type = models.CharField(
        max_length=10, choices=NOTIFICATION_TYPE_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    like_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='likes_given',
        null=True,
        blank=True
    )

    def __str__(self):
        if self.like_user:
            return f"{self.like_user.username} curtiu seu post '{
                self.post.text[:30]}...'"
        else:
            return f"Erro: Like sem usuário associado no post '{
                self.post.text[:30]}...'"
