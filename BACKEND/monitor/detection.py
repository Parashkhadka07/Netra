import os
import joblib
import pandas as pd
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import TrafficEvent

_model = None

def get_model():
    global _model
    if _model is None:
        model_path = os.path.join(settings.BASE_DIR, 'anomaly_model.pkl')
        _model = joblib.load(model_path)
    return _model


FEATURE_ORDER = [
    'connections_per_sec',
    'unique_ports_touched',
    'unique_dst_ips',
    'avg_bytes_per_connection',
    'total_bytes',
]


def extract_features(src_ip, window_seconds=10):
    """Aggregate recent TrafficEvent rows for one source IP into the same
    feature shape the model was trained on."""
    since = timezone.now() - timedelta(seconds=window_seconds)
    events = TrafficEvent.objects.filter(src_ip=src_ip, timestamp__gte=since)

    count = events.count()
    if count == 0:
        return None

    total_bytes = sum(e.bytes_transferred for e in events)
    avg_bytes = total_bytes / count

    return {
        'connections_per_sec': count / window_seconds,
        'unique_ports_touched': events.values('port').distinct().count(),
        'unique_dst_ips': events.values('dst_ip').distinct().count(),
        'avg_bytes_per_connection': avg_bytes,
        'total_bytes': total_bytes,
    }


def score_traffic(features_dict):
    model = get_model()
    # Build as a DataFrame with named columns — matches the format
    # the model was trained on, removes the "no valid feature names" warning
    X = pd.DataFrame([features_dict])[FEATURE_ORDER]

    prediction = model.predict(X)[0]           # -1 = anomaly, 1 = normal
    raw_score = model.decision_function(X)[0]   # lower = more anomalous

    is_anomaly = prediction == -1
    # rough normalization into a 0-1 risk score for display purposes
    risk_score = max(0.0, min(1.0, 0.5 - raw_score))

    return is_anomaly, risk_score


def classify_anomaly(features_dict):
    if features_dict['unique_ports_touched'] > 15:
        return "Port Scan"
    elif features_dict['connections_per_sec'] > 50:
        return "DDoS / Traffic Spike"
    elif features_dict['total_bytes'] > 1_000_000:
        return "Possible Data Exfiltration"
    return "Unusual Traffic Pattern"