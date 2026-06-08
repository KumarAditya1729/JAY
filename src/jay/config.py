from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env: str = Field(default="local", validation_alias="JAY_ENV")
    founder_id: str = Field(default="founder", validation_alias="JAY_FOUNDER_ID")
    database_url: str = Field(
        default="postgresql+psycopg://jay:jay_local_password@localhost:5432/jay",
        validation_alias="DATABASE_URL",
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
