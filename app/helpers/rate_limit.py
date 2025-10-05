
import time
from typing import Tuple
import redis
from app.core.config import settings

d = True if settings.MODE == "Development" else False
r = redis.from_url(settings.CELERY_BROKER_URL if not d else settings.CELERY_BROKER_URL_EXTERNAL)
  # you already use Redis

def _key(prefix: str, email: str, ip: str) -> str:
    return f"{prefix}:{email.lower()}:{ip}"

def allow(prefix: str, email: str, ip: str, max_attempts: int, window_sec: int) -> bool:
    k = _key(prefix, email, ip)
    with r.pipeline() as p:
        p.incr(k)
        p.expire(k, window_sec)
        count, _ = p.execute()
    return int(count) <= max_attempts
