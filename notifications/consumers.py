import json
import logging
from django.utils.timezone import now
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer  # 🔹 FIX: Missing import
from .models import NotificationPreference, Notification

logger = logging.getLogger(__name__)  # Logging setup

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handles WebSocket connection"""
        self.user = self.scope.get("user")

        if not self.user or not self.user.is_authenticated:
            await self.close()
            return

        # Check if user has web notifications enabled
        try:
            prefs = NotificationPreference.objects.get(user=self.user)
            if not prefs.web_notifications:
                await self.close()
                return
        except NotificationPreference.DoesNotExist:
            pass  # Use default settings if no preferences exist

        self.group_name = f"user_{self.user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        logger.info(f"WebSocket connected: {getattr(self.user, 'username', 'Unknown')}")  # 🔹 FIX: Avoid NoneType errors

    async def disconnect(self, close_code):
        """Handles WebSocket disconnection"""
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            logger.info(f"WebSocket disconnected: {getattr(self.user, 'username', 'Unknown')}")

    async def send_notification(self, event):
        """Send real-time notifications via WebSocket"""
        try:
            # Map notification data to match Notification model fields
            notification_data = {
                "id": event.get("notification_id"),
                "title": event["title"],
                "message": event["message"],
                "timestamp": event["timestamp"],
                "notification_type": event.get("notification_type", "system"),
                "source_id": event.get("source_id"),
                "source_model": event.get("source_model"),
                "priority": event.get("priority", 0),
                "ai_enhanced": event.get("is_ai_enhanced", False),
                "ai_insights": event.get("ai_insights"),
                "is_read": False
            }

            # Validate notification type against model choices
            if notification_data["notification_type"] not in dict(Notification.NOTIFICATION_TYPES):
                notification_data["notification_type"] = "system"

            await self.send(text_data=json.dumps(notification_data))
            logger.debug(f"Notification sent to {getattr(self.user, 'username', 'Unknown')}: {notification_data['title']}")

        except json.JSONDecodeError as e:
            logger.error(f"JSON decoding error: {str(e)}")
        except AttributeError as e:
            logger.error(f"Attribute error in WebSocket notification: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected WebSocket error: {str(e)}")
