from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Database Settings
    database_url: str = Field(default="postgresql://user:password@host.docker.internal:5432/omniscraper", env="DATABASE_URL")
    
    # RabbitMQ Settings
    rabbitmq_url: str = Field(default="amqp://guest:guest@localhost:5672//", env="RABBITMQ_URL")
    
    # Redis Settings
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # Facebook Settings
    fb_graph_tokens: str = Field(default="", env="FB_GRAPH_TOKENS")
    fb_cookies: str = Field(default="", env="FB_COOKIES")
    
    # TikTok Settings
    tiktok_loop_count: int = Field(default=3, env="TIKTOK_LOOP_COUNT")

    class Config:
        env_file = ".env"


settings = Settings()
