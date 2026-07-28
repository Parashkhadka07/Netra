from django.contrib import admin
from .models import Device

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('device_name', 'ip_address', 'owner', 'created_at')
    list_filter = ('owner',)
    search_fields = ('device_name', 'ip_address')