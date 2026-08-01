from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient
from .models import Device


class MonitorApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='admin', password='password123')
        self.device = Device.objects.create(
            owner=self.user,
            device_name='Test Sensor',
            ip_address='10.0.0.5',
            location='Lab',
        )

    def test_registration_and_login(self):
        response = self.client.post('/api/auth/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'StrongPassword!23',
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('token', response.data)

        response = self.client.post('/api/auth/login/', {
            'username': 'newuser',
            'password': 'StrongPassword!23',
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

    def test_simulate_attack_requires_auth(self):
        response = self.client.post('/api/simulate_attack/', {'device_id': self.device.id, 'attack_type': 'port_scan'}, format='json')
        self.assertEqual(response.status_code, 401)

    def test_simulate_attack_creates_events(self):
        self.client.force_authenticate(self.user)
        response = self.client.post('/api/simulate_attack/', {'device_id': self.device.id, 'attack_type': 'port_scan'}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('attack_type', response.data)
        self.assertGreaterEqual(response.data['created_events'], 1)

# Create your tests here.
