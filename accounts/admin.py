from django.contrib import admin
from .models import OTP, RegistrationNotification, PasswordResetToken


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ['user', 'otp', 'verified', 'attempts', 'created_at', 'expires_at']
    list_filter = ['verified']
    search_fields = ['user__username']
    readonly_fields = ['otp', 'created_at', 'expires_at']


@admin.register(RegistrationNotification)
class RegistrationNotificationAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'registered_at', 'admin_notified']
    list_filter = ['admin_notified', 'registered_at']
    search_fields = ['username', 'email']
    readonly_fields = ['user', 'username', 'email', 'registered_at', 'admin_notified']


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token_short', 'created_at', 'expires_at', 'used']
    list_filter = ['used', 'created_at']
    search_fields = ['user__username']
    readonly_fields = ['token', 'created_at', 'expires_at']

    def token_short(self, obj):
        return f'{obj.token[:12]}...'
    token_short.short_description = 'Token'
