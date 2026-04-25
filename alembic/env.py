"""
alembic/env.py
--------------
Alembic migration environment.

This file is executed by Alembic for every migration command (upgrade,
downgrade, revision, etc.). It is responsible for:
  1. Loading the real DATABASE_URL from the .env file at the project root.
  2. Overriding the placeholder URL in alembic.ini with the live value.
  3. Providing Alembic with the SQLAlchemy metadata (Base.metadata) so that
     autogenerate can diff the current database schema against the ORM models.
  4. Running migrations in either offline or online mode.

Offline mode  — generates raw SQL to stdout; no live DB connection required.
Online mode   — connects to the database and executes migrations directly.
"""

import os
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

from alembic import context

# ---------------------------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------------------------

# Load .env from the project root (one level up from this file) so that
# DATABASE_URL is available in os.environ before anything reads it.
# In production environments where DATABASE_URL is already set as a real
# environment variable, load_dotenv() is a no-op — it never overwrites
# an existing variable.
load_dotenv()

# ---------------------------------------------------------------------------
# Alembic Config object
# ---------------------------------------------------------------------------

# context.config provides access to the values in alembic.ini.
config = context.config

# ---------------------------------------------------------------------------
# Override the database URL
# ---------------------------------------------------------------------------

# Replace the placeholder sqlalchemy.url from alembic.ini with the real
# DATABASE_URL from the environment. This means alembic.ini never contains
# a real credential — it is safe to commit.
# Raises KeyError at migration time if DATABASE_URL is missing, which is
# the correct behaviour: migrations must never run against an unknown target.
config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

# Use the logging configuration defined in the [loggers] / [handlers] /
# [formatters] sections of alembic.ini. Only configured when alembic.ini
# is present (i.e. not when env.py is imported programmatically in tests).
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------------
# Target metadata — required for autogenerate
# ---------------------------------------------------------------------------

# Import the shared declarative Base from database.py. All ORM models must
# import Base from this same object and define their __tablename__ so that
# Alembic can detect new, changed, or dropped tables automatically.
#
# IMPORTANT: every model module must be imported somewhere before this point
# (directly or transitively) so its Table objects are registered on
# Base.metadata. Add explicit imports below as new model files are created.
from database import Base  # noqa: E402

# -- Model imports ----------------------------------------------------------
# Importing each model module registers its Table on Base.metadata.
# Without these imports, autogenerate will see an empty metadata object and
# generate a migration that drops every table.
#
# Add one line per model file as they are implemented:
#   from backend.models.user        import User          # noqa: F401
#   from backend.models.membership  import Membership    # noqa: F401
#   from backend.models.district    import District      # noqa: F401
#   from backend.models.operator    import Operator      # noqa: F401
#   from backend.models.yard        import Yard          # noqa: F401
#   from backend.models.school      import School        # noqa: F401
#   from backend.models.driver      import Driver        # noqa: F401
#   from backend.models.bus         import Bus           # noqa: F401
#   from backend.models.route       import Route         # noqa: F401
#   from backend.models.stop        import Stop          # noqa: F401
#   from backend.models.run         import Run           # noqa: F401
#   from backend.models.student     import Student       # noqa: F401
#   from backend.models.assignments import Assignment    # noqa: F401
#   from backend.models.dispatcher  import Dispatcher    # noqa: F401
#   from backend.models.pretrip     import PreTrip       # noqa: F401
#   from backend.models.posttrip    import PostTrip      # noqa: F401
#   from backend.models.incident    import Incident      # noqa: F401
#   from backend.models.alert       import Alert         # noqa: F401
#   from backend.models.event       import Event         # noqa: F401
#   from backend.models.audit       import Audit         # noqa: F401
#   from backend.models.absence     import Absence       # noqa: F401
#   from backend.models.school_confirmation import SchoolConfirmation  # noqa: F401
#   from backend.models.payroll     import Payroll       # noqa: F401
#   from backend.models.shop        import Shop          # noqa: F401

target_metadata = Base.metadata
"""
Base.metadata holds the Table registry for all imported ORM models.
Alembic compares this against the live database schema to determine what
SQL to emit in autogenerated migration scripts.
"""

# ---------------------------------------------------------------------------
# Offline migration mode
# ---------------------------------------------------------------------------


def run_migrations_offline() -> None:
    """
    Run migrations without a live database connection.

    Alembic emits the migration SQL to stdout (or a file if --sql is used)
    rather than executing it. Useful for:
      - Reviewing migrations before applying them.
      - Generating SQL scripts to hand off to a DBA.
      - CI environments without database access.

    literal_binds=True causes bound parameters to be rendered as literals
    in the output SQL, making the script directly executable by psql.
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


# ---------------------------------------------------------------------------
# Online migration mode
# ---------------------------------------------------------------------------


def run_migrations_online() -> None:
    """
    Run migrations with a live database connection.

    Creates a real SQLAlchemy engine from the URL set above, opens a
    connection, and executes the migration SQL directly against the database.
    This is the default mode when running `alembic upgrade head` in
    development and production.

    NullPool is used instead of the default connection pool so that the
    connection is closed and released immediately after the migration
    completes, rather than being held open in a pool that will never be
    reused (migrations are short-lived processes, not long-running servers).
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


# ---------------------------------------------------------------------------
# Entry point — Alembic selects the mode automatically
# ---------------------------------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
