from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    ALGORITHM: str
    SECRET_KEY: str

settings = Settings()