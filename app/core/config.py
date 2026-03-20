from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "OmniScraper-AI"
    # RMQ Connection structure: amqp://user:password@localhost:5672/
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    # Redis Connection: redis://localhost:6379/1
    REDIS_URL: str = "redis://localhost:6379/1"
    
    # TikTok Settings
    TIKTOK_LOOP_COUNT: int = 5
    
    class Config:
        env_file = ".env"

settings = Settings()
