from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DeviceViewSet, TrafficEventViewSet, AlertViewSet,
    SimulateAttackView,
    RegisterAPIView, LoginAPIView, LogoutAPIView
)

router = DefaultRouter()
router.register('devices', DeviceViewSet, basename='device')
router.register('events', TrafficEventViewSet, basename='event')
router.register('alerts', AlertViewSet, basename='alert')

urlpatterns = [
    path('', include(router.urls)),
    path('simulate_attack/', SimulateAttackView.as_view(), name='api-simulate-attack'),
    path('auth/register/', RegisterAPIView.as_view(), name='api-register'),
    path('auth/login/', LoginAPIView.as_view(), name='api-login'),
    path('auth/logout/', LogoutAPIView.as_view(), name='api-logout'),
]