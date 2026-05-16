# /devpulse/backend/alembic/env.py
from __future__ import annotations

import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

from app.db.models import Base

config = context.config
fileConfig(config.config_file_name)


def get_url() -> str:
    url = os.getenv("SYNC_DATABASE_URL") or os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
    # Alembic's default env is synchronous; if the app URL uses an async driver,
    # translate it to a sync dialect for migrations.
    url = url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    url = url.replace("sqlite+aiosqlite://", "sqlite://")
    return url


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(url=url, target_metadata=Base.metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(configuration, prefix="sqlalchemy.", poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
