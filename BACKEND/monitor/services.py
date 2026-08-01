from django.db.models import Count, Q
from .models import Device, TrafficEvent, Alert
from . import detection


def get_user_devices(user):
    return Device.objects.filter(owner=user)


def get_events_for_device(device):
    return TrafficEvent.objects.filter(device=device)


def get_alerts_for_device(device):
    return Alert.objects.filter(event__device=device)


def create_alert(event, alert_type, risk_score):
    return Alert.objects.create(event=event, alert_type=alert_type, risk_score=risk_score)


def devices_ranked_by_risk(user):
    """Complex query 1: devices ranked by number of high-risk alerts (User -> Device -> TrafficEvent -> Alert)."""
    return Device.objects.filter(owner=user).annotate(
        high_risk_count=Count(
            'trafficevent__alert',
            filter=Q(trafficevent__alert__risk_score__gte=0.8)
        )
    ).order_by('-high_risk_count')


def alerts_with_context(user):
    """Complex query 2: alerts joined with device, protocol, and owner info across 4 tables."""
    return Alert.objects.filter(event__device__owner=user).select_related(
        'event__device__owner'
    ).values(
        'id', 'alert_type', 'risk_score', 'resolved',
        'event__protocol', 'event__src_ip', 'event__dst_ip',
        'event__device__id', 'event__device__device_name', 'event__device__owner__username'
    )


from . import detection
from .models import Alert

def process_new_event(event):
    """Call this right after a TrafficEvent is saved."""
    features = detection.extract_features(event.src_ip)
    if features is None:
        return None

    is_anomaly, risk_score = detection.score_traffic(features)

    if is_anomaly:
        alert_type = detection.classify_anomaly(features)
        Alert.objects.create(event=event, alert_type=alert_type, risk_score=risk_score)

    return is_anomaly, risk_score


def simulate_attack(device, attack_type='port_scan'):
    from . import simulator
    return simulator.simulate_attack(device, attack_type)
