from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from channels.db import database_sync_to_async
from .routing import websocket_urlpatterns
from .consumers import NotificationConsumer
from .models import NotificationPreference, Notification
import json

User = get_user_model()

class NotificationConsumerTest(TestCase):
    """Test suite for notification consumers."""

    async def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = await database_sync_to_async(User.objects.create_user)(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Create notification preferences
        self.preferences = await database_sync_to_async(NotificationPreference.objects.create)(
            user=self.user,
            web_notifications=True,
            email_notifications=True,
            push_notifications=True
        )

        # Create test notification
        self.notification = await database_sync_to_async(Notification.objects.create)(
            user=self.user,
            title='Test Notification',
            message='This is a test notification',
            notification_type='system',
            priority=1,
            ai_enhanced=True,
            ai_insights='AI generated insights'
        )

        # Set up WebSocket application
        self.application = URLRouter(websocket_urlpatterns)

    async def test_connect_authenticated(self):
        """Test WebSocket connection with authenticated user."""
        communicator = WebsocketCommunicator(
            self.application,
            '/ws/notifications/',
            {'user': self.user}
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.disconnect()

    async def test_connect_unauthenticated(self):
        """Test WebSocket connection with unauthenticated user."""
        communicator = WebsocketCommunicator(
            self.application,
            '/ws/notifications/',
            {'user': None}
        )
        connected, _ = await communicator.connect()
        self.assertFalse(connected)

    async def test_connect_notifications_disabled(self):
        """Test WebSocket connection with web notifications disabled."""
        # Disable web notifications
        self.preferences.web_notifications = False
        await database_sync_to_async(self.preferences.save)()

        communicator = WebsocketCommunicator(
            self.application,
            '/ws/notifications/',
            {'user': self.user}
        )
        connected, _ = await communicator.connect()
        self.assertFalse(connected)

    async def test_send_notification(self):
        """Test sending notification via WebSocket."""
        communicator = WebsocketCommunicator(
            self.application,
            '/ws/notifications/',
            {'user': self.user}
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send notification
        notification_data = {
            'type': 'send_notification',
            'notification_id': self.notification.id,
            'title': 'Test Notification',
            'message': 'This is a test notification',
            'timestamp': str(timezone.now()),
            'notification_type': 'system',
            'priority': 1,
            'is_ai_enhanced': True,
            'ai_insights': 'AI generated insights'
        }
        await communicator.send_json_to(notification_data)

        # Receive response
        response = await communicator.receive_json_from()
        self.assertEqual(response['title'], 'Test Notification')
        self.assertEqual(response['message'], 'This is a test notification')
        self.assertEqual(response['notification_type'], 'system')
        self.assertEqual(response['priority'], 1)
        self.assertTrue(response['ai_enhanced'])
        self.assertEqual(response['ai_insights'], 'AI generated insights')
        self.assertFalse(response['is_read'])

        await communicator.disconnect()

    async def test_send_invalid_notification_type(self):
        """Test sending notification with invalid notification type."""
        communicator = WebsocketCommunicator(
            self.application,
            '/ws/notifications/',
            {'user': self.user}
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send notification with invalid type
        notification_data = {
            'type': 'send_notification',
            'notification_id': self.notification.id,
            'title': 'Test Notification',
            'message': 'This is a test notification',
            'timestamp': str(timezone.now()),
            'notification_type': 'invalid_type',  # Invalid type
            'priority': 1
        }
        await communicator.send_json_to(notification_data)

        # Receive response - should default to 'system' type
        response = await communicator.receive_json_from()
        self.assertEqual(response['notification_type'], 'system')

        await communicator.disconnect()

    async def test_send_invalid_json(self):
        """Test sending invalid JSON data."""
        communicator = WebsocketCommunicator(
            self.application,
            '/ws/notifications/',
            {'user': self.user}
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Send invalid JSON
        await communicator.send_to(text_data='invalid json')

        # Connection should remain open despite error
        self.assertTrue(communicator.connected)

        await communicator.disconnect()

    async def test_disconnect(self):
        """Test WebSocket disconnection."""
        communicator = WebsocketCommunicator(
            self.application,
            '/ws/notifications/',
            {'user': self.user}
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Disconnect
        await communicator.disconnect()
        self.assertFalse(communicator.connected)
