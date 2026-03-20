from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Kết nối đồng bộ (Sync) cho Celery và FastAPI (cơ bản)
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency để sử dụng trong FastAPI Routers
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
