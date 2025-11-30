from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Flow Manager"
    ENV: str = "dev"

    class Config:
        env_file = ".env"

settings = Settings()
