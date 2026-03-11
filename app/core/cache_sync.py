import redis

from app.core.config import settings

redis_client_sync = redis.from_url(settings.REDIS_URL)
