from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "E-Voting Backend"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_database: str = "e_voting"
    mysql_user: str = "root"
    mysql_password: str = "password"

    database_url: str = "mysql+pymysql://root:password@127.0.0.1:3306/e_voting"

    jwt_secret_key: str = "change-me"
    jwt_access_token_expire_minutes: int = 60

    face_match_threshold: float = 0.35
    face_max_retries: int = 3
    face_model_name: str = "buffalo_l"

    upload_dir: str = "storage"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

