from pydantic_settings import BaseSettings
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Settings(BaseSettings):
    DATABASE_URL: str

    class config:
        env_file = ".env"


settings = Settings()

engine = create_engine(settings.DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoFlush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():

    db = SessionLocal

    try:
        yield db

    finally:
        db.close()
