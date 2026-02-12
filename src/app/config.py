from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict;
from functools import lru_cache

BASE_DIR = Path(__file__).resolve().parents[2]  # project_root

class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env")

    db_host: str
    db_name: str
    db_port: str
    db_username: str
    db_password: str
    db_connect_timeout: int
    db_ssl_mode: str
    jwt_secret_key: str
    jwt_algorithm: str
    jwt_expires_minutes: int
    oauth_token_url: str
    log_level: str

    def get_db_database_url(self) -> str:
        return (
            f"postgresql://{self.db_username}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
            f"?sslmode={self.db_ssl_mode}&connect_timeout={self.db_connect_timeout}"
        )

@lru_cache
def get_config() -> Config:
    return Config()