from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)  # E-mail único

    # Defina related_name para evitar conflitos
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',  # Nome único para o relacionamento reverso
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_permissions_set',  # Nome único para o
        blank=True                                  # relacionamento reverso
    )

    def __str__(self):
        return self.username
