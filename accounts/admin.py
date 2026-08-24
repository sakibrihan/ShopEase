from django.contrib import admin
from .models import OTP


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ['user', 'otp', 'verified', 'attempts', 'created_at', 'expires_at']
    list_filter = ['verified']
    search_fields = ['user__username']
    readonly_fields = ['otp', 'created_at', 'expires_at']
