import json
import logging
from django.utils.timezone import now
from django.core.mail import send_mail
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification, NotificationPreference, User

logger = logging.getLogger(__name__)

def send_notification(user_id, title, message, notification_type="system", source_id=None, source_model=None, priority=0, ai_enhanced=False, ai_insights=None):
    """Creates and sends a notification, respecting user preferences."""

    user = User.objects.filter(id=user_id).first()
    if not user:
        logger.error(f"❌ Failed to send notification - User {user_id} not found")
        return "User not found"

    # Check or create user notification preferences
    prefs, _ = NotificationPreference.objects.get_or_create(user=user)  # 🔹 Prevents missing preferences
    if not prefs.can_send_notification(notification_type):
        logger.info(f"⚠️ User {user.username} has disabled {notification_type} notifications.")
        return f"User has disabled {notification_type} notifications."

    # Create and store the notification
    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        source_id=source_id,
        source_model=source_model,
        priority=priority,
        ai_enhanced=ai_enhanced,
        ai_insights=ai_insights
    )

    # Send email notification if enabled
    if prefs.email_notifications:
        try:
            send_mail(
                subject=title,
                message=message,
                from_email=settings.EMAIL_HOST_USER,  # 🔹 Explicitly use configured email sender
                recipient_list=[user.email],
                fail_silently=False
            )
            logger.info(f"📧 Email notification sent to {user.email}")
        except Exception as e:
            logger.error(f"❌ Failed to send email to {user.email}: {str(e)}")

    # Push real-time notification via WebSockets
    try:
        channel_layer = get_channel_layer()
        if channel_layer is None:  # 🔹 Avoid async_to_sync call if no WebSocket layer exists
            logger.warning("⚠️ WebSocket channel layer is not available. Skipping real-time notification.")
        else:
            notification_data = {
                "type": "send_notification",
                "notification_id": notification.id,
                "title": title,
                "message": message,
                "timestamp": now().isoformat(),
                "notification_type": notification_type,
                "source_id": source_id,
                "source_model": source_model,
                "priority": priority,
                "is_ai_enhanced": ai_enhanced,
                "ai_insights": ai_insights
            }
            async_to_sync(channel_layer.group_send)(
                f"user_{user_id}",
                notification_data
            )
            logger.debug(f"📢 Real-time notification sent to user {user.username}")
    except Exception as e:
        logger.error(f"❌ Failed to send real-time notification: {str(e)}")

    return f"✅ Notification sent to {user.username}"

def some_task_function():
    # Task logic here
    pass

# Remove any Celery-specific logic and call the function directly where needed.
