from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent


class AppSettings(BaseSettings):
    token: str
    db_url: str

    class Config:
        env_file = BASE_DIR / '.env'
        env_prefix = 'APP_'
