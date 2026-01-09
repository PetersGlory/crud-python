"""
Database configuration and session management using SQLAlchemy.

This module provides:
- Database connection setup
- Session management
- Base class for ORM models
- Database initialization utilities
"""

import os
from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Database URL configuration
# Uses SQLite by default for development, can be overridden via DATABASE_URL environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./crud.db"
)

# Engine configuration
# For SQLite, use StaticPool to avoid threading issues in development
if "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # For other databases (PostgreSQL, MySQL, etc.)
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Verify connections before use
        echo=os.getenv("SQL_ECHO", "False").lower() == "true",  # Log SQL statements if enabled
    )

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for ORM models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    
    Usage in FastAPI:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize the database by creating all tables.
    
    This function creates all tables defined in the Base metadata.
    Should be called once during application startup.
    """
    Base.metadata.create_all(bind=engine)


def drop_db() -> None:
    """
    Drop all tables from the database.
    
    WARNING: This is destructive and will delete all data.
    Use with caution, primarily for testing purposes.
    """
    Base.metadata.drop_all(bind=engine)


def reset_db() -> None:
    """
    Reset the database by dropping and recreating all tables.
    
    WARNING: This will delete all existing data.
    Use with caution, primarily for testing and development.
    """
    drop_db()
    init_db()


# SQLite-specific configuration for better performance in development
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign keys for SQLite databases."""
    if "sqlite" in DATABASE_URL:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


if __name__ == "__main__":
    # Initialize database when script is run directly
    print(f"Initializing database: {DATABASE_URL}")
    init_db()
    print("Database initialized successfully!")
