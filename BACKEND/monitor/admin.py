from django.contrib import admin
from .models import Device,TrafficEvent, Alert

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('device_name', 'ip_address', 'owner', 'created_at')
    list_filter = ('owner',)
    search_fields = ('device_name', 'ip_address')

@admin.register(TrafficEvent)
class TrafficEventAdmin(admin.ModelAdmin):
    list_display = ('src_ip', 'dst_ip', 'protocol', 'port', 'device', 'timestamp')
    list_filter = ('protocol', 'device')
    search_fields = ('src_ip', 'dst_ip')


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('alert_type', 'risk_score', 'resolved', 'event', 'created_at')
    list_filter = ('alert_type', 'resolved')