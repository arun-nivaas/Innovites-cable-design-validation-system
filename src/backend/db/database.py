from sqlalchemy import create_engine
from src.backend.config.settings import settings
from sqlalchemy.orm import sessionmaker, declarative_base


engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# FastAPI dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()