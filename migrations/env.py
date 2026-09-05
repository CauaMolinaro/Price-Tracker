import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Garante que "app" seja encontrado ao importar, independente de onde
# o comando alembic for executado a partir da raiz do projeto.
sys.path.insert(0, os.getcwd())

from app.database import Base, DATABASE_URL  # noqa: E402
from app.models.models import Usuario, Produto, HistoricoPreco, Alerta  # noqa: E402,F401

# Objeto de configuração do Alembic, acessa os valores do alembic.ini
config = context.config

# Sobrescreve a URL do banco definida no alembic.ini pela variável
# usada pela própria aplicação (DATABASE_URL em app/database.py),
# assim os dois nunca ficam dessincronizados.
config.set_main_option("sqlalchemy.url", DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata dos models — é o que permite o --autogenerate funcionar
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Gera o SQL sem se conectar de fato ao banco (modo offline)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Conecta ao banco de verdade e aplica as migrações (modo padrão)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection,
                          target_metadata=target_metadata, render_as_batch=True)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
