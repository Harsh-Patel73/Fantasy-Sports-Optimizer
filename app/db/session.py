from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from config import get_config

_engine = None
_SessionLocal = None


def get_engine():
    """Get or create the database engine based on configuration."""
    global _engine
    if _engine is None:
        config = get_config()

        # Build connection arguments based on database type
        connect_args = {}
        if config.DEMO_MODE:
            # SQLite-specific: allow multi-threaded access
            connect_args["check_same_thread"] = False

        _engine = create_engine(
            config.SQLALCHEMY_DATABASE_URI,
            echo=False,
            connect_args=connect_args
        )

        # Enable foreign keys for SQLite
        if config.DEMO_MODE:
            @event.listens_for(_engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.close()

    return _engine


def get_session():
    """Get the session factory."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_engine()
        )
    return _SessionLocal


def reset_engine():
    """Reset the engine and session (useful for testing or mode switching)."""
    global _engine, _SessionLocal
    if _engine:
        _engine.dispose()
    _engine = None
    _SessionLocal = None


# Backwards compatibility with existing code that uses SessionLocal directly
class SessionLocalWrapper:
    """Wrapper to maintain backwards compatibility with existing code."""

    def __call__(self):
        return get_session()()

    def __enter__(self):
        self._session = get_session()()
        return self._session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._session.close()


SessionLocal = SessionLocalWrapper()

# Also expose the engine for backwards compatibility
engine = property(lambda self: get_engine())
