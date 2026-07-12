from pydantic import ValidationError
from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    client_key: str
    token_access: str
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
