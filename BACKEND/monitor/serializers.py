from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Device, TrafficEvent, Alert


class DeviceSerializer(serializers.ModelSerializer):
    high_risk_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Device
        fields = ['id', 'device_name', 'ip_address', 'location', 'created_at', 'high_risk_count']
        read_only_fields = ['id', 'created_at', 'high_risk_count']


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


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user