from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# 1. Define the database URL.
# "sqlite:///./legal_ai.db" means we will use SQLite, and the database file
# will be named "legal_ai.db" in the current directory (which will be the `backend` folder).
SQLALCHEMY_DATABASE_URL = "sqlite:///./legal_ai.db"

# 2. Create the SQLAlchemy "engine".
# The engine is the main entry point for SQLAlchemy to communicate with the database.
# The `connect_args` is needed only for SQLite to allow it to be used by multiple threads,
# which is something FastAPI does.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. Create a SessionLocal class.
# Each instance of SessionLocal will be a new database session. A session is the
# "conversation" you have with your database to perform operations (query, insert, etc.).
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Create a Base class.
# Our ORM models will inherit from this class. It helps SQLAlchemy discover our
# models and map them to the database tables.
class Base(DeclarativeBase):
    pass


# Dependency to get a DB session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()