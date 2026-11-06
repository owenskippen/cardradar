import os
from functools import lru_cache

from pydantic import BaseModel


class Settings(BaseModel):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/cardradar"
    api_prefix: str = "/api"
    admin_api_key: str = "changeme-admin-key"


@lru_cache
def get_settings() -> Settings:
    return Settings(
        database_url=os.getenv("DATABASE_URL", Settings().database_url),
        api_prefix=os.getenv("API_PREFIX", Settings().api_prefix),
        admin_api_key=os.getenv("ADMIN_API_KEY", Settings().admin_api_key),
    )

