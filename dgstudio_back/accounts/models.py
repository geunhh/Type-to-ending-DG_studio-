from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    kakao_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    profile_image = models.URLField(null=True, blank=True)
    nickname = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.username