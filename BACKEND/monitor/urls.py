from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeviceViewSet, TrafficEventViewSet, AlertViewSet

router = DefaultRouter()
router.register('devices', DeviceViewSet, basename='device')
router.register('events', TrafficEventViewSet, basename='event')
router.register('alerts', AlertViewSet, basename='alert')

urlpatterns = [
    path('', include(router.urls)),
]