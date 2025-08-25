from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/emc3_lighting")
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # B2B скидки
    wholesale_discount_5: int = int(os.getenv("WHOLESALE_DISCOUNT_5", "5"))
    wholesale_discount_10: int = int(os.getenv("WHOLESALE_DISCOUNT_10", "10"))
    wholesale_discount_50: int = int(os.getenv("WHOLESALE_DISCOUNT_50", "15"))

settings = Settings()

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()