import os
from dotenv import load_dotenv

from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig

from app.database.base import Base
from app.models.user import User
from app.models.habit import Habit
from app.models.track import Track

load_dotenv()

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


url = os.getenv("ALEMBIC_URL")
if url:
    config.set_main_option("sqlalchemy.url", url)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()