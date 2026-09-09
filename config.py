from functools import lru_cache
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    jira_base_url: str = "https://kamalrajmce.atlassian.net"
    jira_email: str
    jira_api_token: SecretStr
    jira_rca_field: str = "customfield_10043"
    jira_timeout_seconds: float = 30.0

    llm_api_url: str = ""
    llm_api_token: SecretStr
    llm_auth_header: str = "Authorization"
    llm_auth_prefix: str = "Bearer"
    llm_model: str | None = None
    llm_timeout_seconds: float = 60.0
    llm_verify_ssl: bool = True
    mock_llm_mode: bool = True

    app_log_level: str = "INFO"

@lru_cache
def get_settings() -> Settings:
    return Settings()
