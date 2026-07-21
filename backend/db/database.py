from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.config import get_settings

settings = get_settings()

# check_same_thread=False is needed only for SQLite, harmless for other DBs
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency: yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Called once on app startup."""
    # Import models here so they're registered on Base before create_all runs
    from backend.auth import models as auth_models  # noqa: F401
    from backend.admin import models as admin_models  # noqa: F401
    from backend.chat import models as chat_models  # noqa: F401

    Base.metadata.create_all(bind=engine)
