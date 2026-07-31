from django.db.models import Count, Q
from .models import Device, TrafficEvent, Alert

def get_user_devices(user):
    return Device.objects.filter(owner=user)

def get_events_for_device(device):
    return TrafficEvent.objects.filter(device=device)

def get_alerts_for_device(device):
    return Alert.objects.filter(event__device=device)

def create_alert(event, alert_type, risk_score):
    return Alert.objects.create(event=event, alert_type=alert_type, risk_score=risk_score)

# Complex query 1: devices ranked by high-risk alert count
def devices_ranked_by_risk(user):
    return Device.objects.filter(owner=user).annotate(
        high_risk_count=Count('trafficevent__alert', filter=Q(trafficevent__alert__risk_score__gte=0.8))
    ).order_by('-high_risk_count')

# Complex query 2: full alert context across 4 linked tables
def alerts_with_context(user):
    return Alert.objects.filter(event__device__owner=user).select_related(
        'event__device__owner'
    ).values(
        'alert_type', 'risk_score', 'event__protocol',
        'event__device__device_name', 'event__device__owner__username'
    )