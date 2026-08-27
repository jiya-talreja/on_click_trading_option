from pydantic import ValidationError
from pydantic_settings import BaseSettings
from dhanhq import DhanLogin
import pyotp
class Settings(BaseSettings):
    client_key: str
    access_token:str
    upstox_access_token:str
    redis_host:str
    redis_port:int
    redis_db:int
    redis_timeout:int
    redis_max_connection:int
    class Config:
        env_file = ".env"
try:
    settings = Settings()
except ValidationError as e:
    raise RuntimeError(f"Configuration error:\n{e}")
