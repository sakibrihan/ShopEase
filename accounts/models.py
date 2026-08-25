import secrets
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class OTP(models.Model):
    """Demo OTP model for account verification."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='otp')
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    verified = models.BooleanField(default=False)
    attempts = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'OTP for {self.user.username}'

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=5)
        super().save(*args, **kwargs)


class RegistrationNotification(models.Model):
    """Records every new user registration and tracks admin notification."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='registration_notification')
    username = models.CharField(max_length=150)
    email = models.EmailField()
    registered_at = models.DateTimeField(auto_now_add=True)
    admin_notified = models.BooleanField(default=False)

    class Meta:
        ordering = ['-registered_at']

    def __str__(self):
        return f'Registration: {self.username} ({self.email})'


class PasswordResetToken(models.Model):
    """Secure token for password reset via email verification."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_tokens')
    token = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    def __str__(self):
        return f'Reset token for {self.user.username}'

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        return not self.used and not self.is_expired

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(48)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=1)
        super().save(*args, **kwargs)
