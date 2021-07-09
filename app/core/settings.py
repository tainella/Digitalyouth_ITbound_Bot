from pydantic import BaseSettings


class Settings(BaseSettings):
    telegram_api: str
    sqlite_dsn: str = "sqlite:///app/db_data/main.sqlite3"

    class Config:
        case_sensitive = False
        env_file = '.env'
        env_file_encoding = 'utf-8'
