from django.db import models
from django.contrib.auth.models import User

class Device(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    device_name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    location = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.device_name


class TrafficEvent(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    src_ip = models.GenericIPAddressField()
    dst_ip = models.GenericIPAddressField()
    protocol = models.CharField(max_length=10)
    port = models.IntegerField()
    bytes_transferred = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.src_ip} -> {self.dst_ip} ({self.protocol})"


class Alert(models.Model):
    event = models.ForeignKey(TrafficEvent, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=100)
    risk_score = models.FloatField()
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.alert_type} ({self.risk_score})"