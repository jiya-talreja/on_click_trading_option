import json
import redis
from core.config import settings

redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    decode_responses=True,
    socket_timeout=settings.redis_timeout,
    max_connections=settings.redis_max_connection
    )
try:
    redis_client.ping()
    print("Redis Connected Successfully")
except Exception as e:
     print(e)
def save_position(position: dict):
    position_id=position["position_id"]
    key=f"ap:{position_id}"
    position_json=json.dumps(position)
    redis_client.set(
        key,position_json
    )
def get_position(position_id):
    key=f"ap:{position_id}"
    position_json=redis_client.get(
        key
    )
    position=json.loads(position_json)
    return position
