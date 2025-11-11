# alembic/env.py
from alembic import context
from sqlalchemy import engine_from_config, pool
import os

# --- 앱의 Base 메타데이터 import (자동 생성하려면 필요)
from app.database import Base  # Base = declarative_base() 한 객체
target_metadata = Base.metadata

config = context.config

# DB URL: 환경변수 우선, 없으면 기본값
db_url = os.getenv("DATABASE_URL", "sqlite:///./app.db")
config.set_main_option("sqlalchemy.url", db_url)

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,  # ✅ SQLite ALTER 호환용
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,  # ✅ SQLite ALTER 호환용
        )

        with context.begin_transaction():
            context.run_migrations()
