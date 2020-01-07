from django.db import models
from django.contrib.auth.models import AbstractUser

class SiteUser(AbstractUser):
    email = models.EmailField(
        verbose_name='Email Address',
        max_length=64,
        unique=True,
    )

    # user details
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=32)

    # challenge details
    completed_challenges = models.TextField(blank=True)
    upcoming_challenges = models.TextField(blank=True)

    # stats
    stats = models.TextField(blank=True)
    history = models.TextField(blank=True)

    is_premium = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email
