import json
import logging
from typing import List, Optional
import redis.asyncio as aioredis
from app.config import settings
from app.schemas import Message

logger = logging.getLogger(__name__)


class RedisService:
    def __init__(self):
        self.redis_client: Optional[aioredis.Redis] = None

    async def get_client(self) -> aioredis.Redis:
        if self.redis_client is None:
            self.redis_client = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                encoding="utf-8"
            )
        return self.redis_client

    async def close(self):
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None

    def _get_key(self, session_id: str) -> str:
        return f"chat:{session_id}"

    async def save_message(self, session_id: str, message: Message):
        """Save a single message to Redis with TTL and automatic list append."""
        try:
            client = await self.get_client()
            key = self._get_key(session_id)
            serialized = json.dumps({"role": message.role, "content": message.content})
            
            # Append message to list
            await client.rpush(key, serialized)
            
            # Set TTL (default 24h)
            ttl_seconds = settings.REDIS_TTL_HOURS * 3600
            await client.expire(key, ttl_seconds)
        except Exception as e:
            logger.error(f"Error saving message to Redis for session {session_id}: {e}")

    async def get_history(self, session_id: str, limit: Optional[int] = None) -> List[Message]:
        """
        Get chat history with sliding window limit.
        If limit is provided, only retrieves the last `limit` messages.
        """
        try:
            client = await self.get_client()
            key = self._get_key(session_id)
            
            if limit is not None and limit > 0:
                # Sliding window: fetch only the last `limit` items
                raw_messages = await client.lrange(key, -limit, -1)
            else:
                raw_messages = await client.lrange(key, 0, -1)

            messages = []
            for item in raw_messages:
                data = json.loads(item)
                messages.append(Message(role=data["role"], content=data["content"]))
            return messages
        except Exception as e:
            logger.error(f"Error reading history from Redis for session {session_id}: {e}")
            return []

    async def clear_history(self, session_id: str) -> bool:
        """Clear conversation history for a session."""
        try:
            client = await self.get_client()
            key = self._get_key(session_id)
            await client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error clearing history for session {session_id}: {e}")
            return False

    async def get_all_sessions(self) -> List[str]:
        """Get list of active session IDs."""
        try:
            client = await self.get_client()
            keys = await client.keys("chat:*")
            return [k.replace("chat:", "") for k in keys]
        except Exception as e:
            logger.error(f"Error fetching sessions from Redis: {e}")
            return []


redis_service = RedisService()
