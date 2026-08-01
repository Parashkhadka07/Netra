from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TrafficEvent
from . import services

@receiver(post_save, sender=TrafficEvent)
def run_detection_on_new_event(sender, instance, created, **kwargs):
    if created:
        services.process_new_event(instance)