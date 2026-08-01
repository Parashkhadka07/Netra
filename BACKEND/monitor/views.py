from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

from .models import Device, TrafficEvent, Alert
from .serializers import (
    DeviceSerializer, TrafficEventSerializer, AlertSerializer, RegisterSerializer
)
from . import services


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
        # Traffic events are displayed in the shared dashboard.
        return TrafficEvent.objects.select_related('device').all()


class AlertViewSet(viewsets.ModelViewSet):
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Alerts are shared across the dashboard so users can see all incident context.
        return Alert.objects.select_related('event', 'event__device').all()

    @action(detail=False, methods=['get'])
    def with_context(self, request):
        return Response(list(services.alerts_with_context(request.user)))


class SimulateAttackView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        device_id = request.data.get('device_id')
        attack_type = request.data.get('attack_type', 'port_scan')

        try:
            device = Device.objects.get(id=device_id)
        except Device.DoesNotExist:
            return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)

        if device.owner != request.user:
            return Response({'error': 'Device does not belong to the authenticated user'}, status=status.HTTP_403_FORBIDDEN)

        result = services.simulate_attack(device, attack_type)
        return Response(result, status=status.HTTP_201_CREATED)


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'username': user.username}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'username': user.username})
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({'message': 'Logged out'})