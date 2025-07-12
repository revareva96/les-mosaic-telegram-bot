import asyncio
import os

from logging.config import fileConfig

import asyncpg
from sqlalchemy import engine_from_config
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import pool
from urllib.parse import urlparse

from alembic import context
from src.infrastructure.db.models import Base

config = context.config

target_metadata = Base.metadata

db_url = os.environ.get('APP_DB_URL')


if config.config_file_name is not None:
    fileConfig(config.config_file_name)

if not db_url:
    raise RuntimeError('APP_DB_URL not configured')
config.set_main_option('sqlalchemy.url', db_url)


async def create_db():
    dbc = urlparse(db_url)
    db_name = dbc.path.lstrip('/')
    conn = await asyncpg.connect(
        host=dbc.hostname,
        port=dbc.port,
        user=dbc.username,
        password=dbc.password,
        database='postgres'
    )
    try:
        await conn.execute(
            f'CREATE DATABASE {db_name};'
        )
    except asyncpg.exceptions.DuplicateDatabaseError:
        print('Database already exists')
    finally:
        await conn.close()


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


def run_sync_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    await create_db()
    engine = AsyncEngine(
        engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True,
            isolation_level='AUTOCOMMIT'
        )
    )

    async with engine.connect() as connection:
        await connection.run_sync(run_sync_migrations)

    await engine.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
