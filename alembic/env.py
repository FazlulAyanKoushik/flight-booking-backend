from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

import os
import sys
from logging.config import fileConfig
from sqlalchemy import pool
from alembic import context
from sqlalchemy.ext.asyncio import AsyncEngine
from app.models.user import Base

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


import asyncio
import time
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy import text

async def create_engine_with_retry(url, max_retries=10, retry_interval=2):
    """Create a database engine with retry logic for PostgreSQL connections"""
    for attempt in range(max_retries):
        try:
            engine = create_async_engine(url, poolclass=pool.NullPool)
            # Test the connection
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            print(f"Alembic: Database connection established successfully on attempt {attempt + 1}")
            return engine
        except OperationalError as e:
            if attempt < max_retries - 1:
                print(f"Alembic: Database connection attempt {attempt + 1} failed: {str(e)}")
                print(f"Alembic: Retrying in {retry_interval} seconds...")
                await asyncio.sleep(retry_interval)
            else:
                print(f"Alembic: Failed to connect to database after {max_retries} attempts")
                raise

def run_migrations_online() -> None:
    """Run migrations in 'online' mode with async engine."""
    configuration = config.get_section(config.config_ini_section)
    url = os.getenv("DATABASE_URL") or configuration.get("sqlalchemy.url")
    if not url:
        # fallback to your app's db.py logic
        from app.db import DATABASE_URL
        url = DATABASE_URL
    
    async def get_connectable():
        # Use retry logic for database connection
        return await create_engine_with_retry(url)
    
    # Run the async function to get the connectable with retry logic
    connectable = asyncio.run(get_connectable())

    def run_migrations(sync_conn):
        context.configure(connection=sync_conn, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

    async def run_async_migrations():
        async with connectable.connect() as connection:
            await connection.run_sync(run_migrations)

    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
