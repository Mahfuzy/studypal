from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch
import json

User = get_user_model()

class AccountsViewsTest(APITestCase):
    """Test suite for accounts views."""

    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_register(self):
        """Test user registration."""
        url = '/api/accounts/register/'
        data = {
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('user' in response.data)
        self.assertTrue('access_token' in response.data)
        self.assertTrue('refresh_token' in response.data)
        self.assertEqual(response.data['user']['email'], 'newuser@example.com')
        self.assertEqual(User.objects.count(), 2)

    def test_login(self):
        """Test user login."""
        url = '/api/accounts/login/'
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('user' in response.data)
        self.assertTrue('access_token' in response.data)
        self.assertTrue('refresh_token' in response.data)
        self.assertEqual(response.data['user']['email'], 'test@example.com')

    def test_password_change(self):
        """Test password change."""
        url = '/api/accounts/password-change/'
        self.client.force_authenticate(user=self.user)
        data = {
            'old_password': 'testpass123',
            'new_password': 'newtestpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Password changed successfully')

        # Test login with new password
        login_url = '/api/accounts/login/'
        login_data = {
            'email': 'test@example.com',
            'password': 'newtestpass123'
        }
        response = self.client.post(login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('requests.get')
    def test_google_auth(self, mock_get):
        """Test Google authentication."""
        url = '/api/accounts/google/'
        mock_response = {
            'email': 'google@example.com',
            'given_name': 'Google',
            'family_name': 'User'
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response

        data = {
            'id_token': 'fake_google_token'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('user' in response.data)
        self.assertTrue('access_token' in response.data)
        self.assertTrue('refresh_token' in response.data)
        self.assertEqual(response.data['user']['email'], 'google@example.com')
        self.assertEqual(response.data['message'], 'Authenticated')

    def test_user_list(self):
        """Test user listing."""
        url = '/api/accounts/users/'
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['email'], 'test@example.com')

    def test_unauthorized_access(self):
        """Test unauthorized access to protected endpoints."""
        # Test password change without authentication
        url = '/api/accounts/password-change/'
        data = {
            'old_password': 'testpass123',
            'new_password': 'newtestpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test user list without authentication
        url = '/api/accounts/users/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_login(self):
        """Test login with invalid credentials."""
        url = '/api/accounts/login/'
        data = {
            'email': 'test@example.com',
            'password': 'wrongpass'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_password_change(self):
        """Test password change with invalid old password."""
        url = '/api/accounts/password-change/'
        self.client.force_authenticate(user=self.user)
        data = {
            'old_password': 'wrongpass',
            'new_password': 'newtestpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid old password')
