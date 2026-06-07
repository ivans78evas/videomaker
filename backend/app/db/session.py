from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

try:
    engine = create_engine(settings.database_url)
    engine.connect()
except:
    engine = create_engine("sqlite:///./test.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
