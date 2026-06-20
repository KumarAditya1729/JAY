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
    voice_model: str = Field(
        default="en-GB-RyanNeural", validation_alias="JAY_VOICE_MODEL"
    )
    llm_model: str = Field(default="llama3", validation_alias="JAY_LLM_MODEL")
    llm_model_path: str = Field(
        default="models/Meta-Llama-3-8B-Instruct.Q8_0.gguf", validation_alias="JAY_LLM_MODEL_PATH"
    )
    api_key: str = Field(
        default="dev_key_only_change_in_prod", validation_alias="JAY_API_KEY"
    )
    github_token: str | None = Field(default=None, validation_alias="GITHUB_TOKEN")
    bottleneck_multiplier: float = Field(default=0.5, validation_alias="JAY_BOTTLENECK_MULTIPLIER")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
