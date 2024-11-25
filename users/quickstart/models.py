from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    class Meta:
        app_label = "quickstart"

    profile_picture = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
