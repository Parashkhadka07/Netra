from rest_framework import serializers
from .models import Device,TrafficEvent,Alert


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = ['id', 'device_name', 'ip_address', 'location', 'created_at']
        read_only_fields = ['id', 'created_at']

class TrafficEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrafficEvent
        fields = ['id', 'device', 'src_ip', 'dst_ip', 'protocol', 'port', 'bytes_transferred', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = ['id', 'event', 'alert_type', 'risk_score', 'resolved', 'created_at']
        read_only_fields = ['id', 'created_at']