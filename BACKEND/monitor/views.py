from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Device, TrafficEvent, Alert
from .serializers import DeviceSerializer, TrafficEventSerializer, AlertSerializer
from . import services


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('device-list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})



class DeviceViewSet(viewsets.ModelViewSet):
    serializer_class = DeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return services.get_user_devices(self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['get'])
    def events(self, request, pk=None):
        device = self.get_object()
        events = services.get_events_for_device(device)
        return Response(TrafficEventSerializer(events, many=True).data)

    @action(detail=True, methods=['get'])
    def alerts(self, request, pk=None):
        device = self.get_object()
        alerts = services.get_alerts_for_device(device)
        return Response(AlertSerializer(alerts, many=True).data)

    @action(detail=False, methods=['get'])
    def ranked_by_risk(self, request):
        devices = services.devices_ranked_by_risk(request.user)
        return Response(DeviceSerializer(devices, many=True).data)


class TrafficEventViewSet(viewsets.ModelViewSet):
    serializer_class = TrafficEventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TrafficEvent.objects.filter(device__owner=self.request.user)


class AlertViewSet(viewsets.ModelViewSet):
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Alert.objects.filter(event__device__owner=self.request.user)

    @action(detail=False, methods=['get'])
    def with_context(self, request):
        return Response(list(services.alerts_with_context(request.user)))