from pydantic import BaseSettings;

class Config(BaseSettings):
    database_url: str
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

    class Config:
        # Load variables from .env file
        env_file = "../.env"

config = Config()