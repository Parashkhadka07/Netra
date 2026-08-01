import random
from django.utils import timezone
from .models import TrafficEvent


def _random_ip(prefix=None):
    if prefix:
        return f"{prefix}{random.randint(2, 254)}"
    return f"{random.randint(11, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"


def _create_event(device, src_ip, dst_ip, protocol, port, bytes_transferred):
    return TrafficEvent.objects.create(
        device=device,
        src_ip=src_ip,
        dst_ip=dst_ip,
        protocol=protocol,
        port=port,
        bytes_transferred=bytes_transferred,
        timestamp=timezone.now(),
    )


def simulate_port_scan(device, src_ip=None, target_ip=None, count=24):
    src_ip = src_ip or _random_ip('192.168.1.')
    target_ip = target_ip or _random_ip('10.0.0.')
    events = []
    for port in range(20, 20 + count):
        events.append(
            _create_event(
                device=device,
                src_ip=src_ip,
                dst_ip=target_ip,
                protocol='TCP',
                port=port,
                bytes_transferred=random.randint(40, 180),
            )
        )
    return {
        'attack_type': 'port_scan',
        'src_ip': src_ip,
        'target_ip': target_ip,
        'created_events': len(events),
    }


def simulate_ddos(device, src_ip=None, target_ip=None, count=80):
    src_ip = src_ip or _random_ip('192.168.1.')
    target_ip = target_ip or _random_ip('10.0.0.')
    events = []
    for _ in range(count):
        events.append(
            _create_event(
                device=device,
                src_ip=src_ip,
                dst_ip=target_ip,
                protocol='TCP',
                port=random.choice([80, 443, 8080, 53, 22]),
                bytes_transferred=random.randint(600, 1800),
            )
        )
    return {
        'attack_type': 'ddos',
        'src_ip': src_ip,
        'target_ip': target_ip,
        'created_events': len(events),
    }


def simulate_normal_traffic(device, src_ip=None, count=18):
    src_ip = src_ip or _random_ip('192.168.1.')
    events = []
    for _ in range(count):
        events.append(
            _create_event(
                device=device,
                src_ip=src_ip,
                dst_ip=_random_ip('10.0.0.'),
                protocol=random.choice(['TCP', 'UDP', 'ICMP']),
                port=random.choice([53, 80, 443, 123, 3389, 8080]),
                bytes_transferred=random.randint(120, 1400),
            )
        )
    return {
        'attack_type': 'normal',
        'src_ip': src_ip,
        'created_events': len(events),
    }


def simulate_attack(device, attack_type='port_scan'):
    attack_type = (attack_type or 'port_scan').lower()
    if attack_type == 'ddos':
        return simulate_ddos(device)
    if attack_type == 'normal':
        return simulate_normal_traffic(device)
    return simulate_port_scan(device)
