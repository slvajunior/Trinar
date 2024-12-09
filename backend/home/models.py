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
        ("follow", "Follow"),
        ("repost", "Repost"),
        # outros tipos...
    ]
    notification_type = models.CharField(
        max_length=10, choices=NOTIFICATION_TYPE_CHOICES
    )
    created_at = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)

    like_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="likes_given",
        null=True,
        blank=True,
    )

    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="followers_notifications",
        null=True,
        blank=True,
    )

    repost_user = models.ForeignKey(  # Novo campo
        User,
        on_delete=models.CASCADE,
        related_name="reposts_notifications",
        null=True,
        blank=True,
    )

    def __str__(self):
        if self.notification_type == "like" and self.like_user:
            return f"{self.like_user.username} curtiu seu post '{
                self.post.text[:30]}...'"
        elif self.notification_type == "follow" and self.follower:
            return f"{self.follower.username} começou a seguir você."
        elif self.notification_type == "repost":
            return f"Seu post foi repostado por {self.user.username}."
        else:
            return "Erro na notificação."


class Follow(models.Model):
    follower = models.ForeignKey(
        User, related_name="user_following", on_delete=models.CASCADE
    )
    following = models.ForeignKey(
        User, related_name="user_followers", on_delete=models.CASCADE
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "following")

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"
