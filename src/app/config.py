from pathlib import Path
from pydantic import ValidationError
from pydantic_settings import BaseSettings;
from functools import lru_cache

BASE_DIR = Path(__file__).resolve().parents[2]  # project_root

class Config(BaseSettings):
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
    db_database_url: str = f"postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"

    class Config:
        # Load variables from .env file
        env_file =  BASE_DIR / ".env"

@lru_cache
def get_config() -> Config:
    return Config()