from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    full_name = models.CharField(max_length=255, blank=True)
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", blank=True, null=True
    )
    bio = models.TextField(blank=True, null=True)
    locale = models.CharField(max_length=255, blank=True)
    born = models.DateField(null=True, blank=True)
    joined_in = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} Profile"


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    image = models.ImageField(upload_to='post_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField()
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    class Meta:
        ordering = ['-created_at']  # Ordenando pelos posts mais recentes

    def __str__(self):
        location_info = f'from {self.location}' if self.location else ""
        return f"Post by {self.user.username} at {self.created_at}{location_info}"
