import os
import time
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from sqlalchemy import text

DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite3")

if DATABASE_TYPE == "sqlite3":
    SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "./app.db")
    DATABASE_URL = f"sqlite+aiosqlite:///{SQLITE_DB_PATH}"
else:
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Create engine with connection retry logic
async def create_db_engine_with_retry(url, max_retries=10, retry_interval=2):
    """Create a database engine with retry logic for PostgreSQL connections"""
    for attempt in range(max_retries):
        try:
            engine = create_async_engine(url, echo=False)
            # Test the connection
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            print(f"Database connection established successfully on attempt {attempt + 1}")
            return engine
        except OperationalError as e:
            if attempt < max_retries - 1:
                print(f"Database connection attempt {attempt + 1} failed: {str(e)}")
                print(f"Retrying in {retry_interval} seconds...")
                await asyncio.sleep(retry_interval)
            else:
                print(f"Failed to connect to database after {max_retries} attempts")
                raise

# Create engine based on database type
if DATABASE_TYPE == "sqlite3":
    engine = create_async_engine(DATABASE_URL, echo=False)
else:
    # For PostgreSQL, we'll initialize the engine later with retry logic
    engine = None

# Create session factory
async_session = sessionmaker(class_=AsyncSession, expire_on_commit=False)

# Initialize engine and bind session factory
async def initialize_db():
    global engine
    if DATABASE_TYPE != "sqlite3" and engine is None:
        engine = await create_db_engine_with_retry(DATABASE_URL)
        async_session.configure(bind=engine)
    elif engine is None:
        # For SQLite, just configure the session with the already created engine
        async_session.configure(bind=engine)
