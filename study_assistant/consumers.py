import json
import logging
import os
from typing import Optional, Dict, Any
from channels.generic.websocket import AsyncWebsocketConsumer
from google import genai
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

# Ensure API key is set
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

class TaeAIConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id: Optional[str] = None
        self.chat = None
        self.message_count = 0
        self.last_message_time = None
        self.MAX_MESSAGES_PER_MINUTE = 30
        self.client = None  # Initialize client inside connect()

    async def connect(self):
        """Handle WebSocket connection setup."""
        try:
            # Initialize Gemini client
            self.client = genai.Client(api_key=GEMINI_API_KEY)

            # Get user ID or set as guest
            user = self.scope.get("user")
            self.user_id = str(user.id) if user and user.is_authenticated else "guest"

            # Initialize chat session
            self.chat = self.client.chats.create(model="gemini-2.0-flash")

            logger.info(f"WebSocket connected for user {self.user_id}")
            await self.accept()
        except Exception as e:
            logger.error(f"Error in WebSocket connection: {str(e)}")
            await self.close()

    async def receive(self, text_data: str = None):
        """Handle incoming WebSocket messages (text only)."""
        try:
            if not text_data:
                await self.send(json.dumps({"error": "Empty message received"}))
                return

            # Validate message format
            try:
                data = json.loads(text_data)
            except json.JSONDecodeError:
                await self.send(json.dumps({"error": "Invalid JSON format"}))
                return

            prompt = data.get("query")
            if not prompt or not isinstance(prompt, str):
                await self.send(json.dumps({"error": "Invalid query format"}))
                return

            # Rate limiting
            if not self._check_rate_limit():
                await self.send(json.dumps({"error": "Rate limit exceeded"}))
                return

            response = await self._get_ai_response(prompt)
            self.message_count += 1
            self.last_message_time = datetime.now()

            await self.send(json.dumps({
                "response": response,
                "timestamp": self.last_message_time.isoformat()
            }))

        except Exception as e:
            logger.error(f"❌ Error processing message: {str(e)}")
            await self.send(json.dumps({"error": "An internal error occurred"}))

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        logger.info(f"WebSocket disconnected for user {self.user_id}")

    def _check_rate_limit(self) -> bool:
        """Check if user has exceeded rate limit."""
        if not self.last_message_time:
            return True

        time_since_last_message = (datetime.now() - self.last_message_time).total_seconds()
        if time_since_last_message >= 60:
            self.message_count = 0

        return self.message_count < self.MAX_MESSAGES_PER_MINUTE

    async def _get_ai_response(self, prompt: str) -> str:
        """Get response from AI model with error handling."""
        try:
            response = self.chat.send_message(prompt)
            return response.text
        except Exception as e:
            logger.error(f"AI model error: {str(e)}")
            return "Failed to get AI response"
