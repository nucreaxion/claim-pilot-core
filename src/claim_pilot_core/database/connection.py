"""
Claim Pilot Core - Database Connection

PostgreSQL connection management with connection pooling,
query execution helpers, transaction support, and performance logging.
"""

import time
from contextlib import contextmanager
from typing import Any, Dict, Generator, List, Optional

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor

from ..core.config import get_settings
from ..core.exceptions import DatabaseError
from ..core.logging import get_logger

logger = get_logger(__name__)


class DatabaseConnection:
    """
    PostgreSQL connection wrapper with connection pooling.

    Usage:
        db = DatabaseConnection()
        rows = db.fetch_all("SELECT * FROM claims WHERE id = %s", (claim_id,))
        row = db.fetch_one("SELECT * FROM policies WHERE id = %s", (policy_id,))
        db.execute("UPDATE claims SET status = %s WHERE id = %s", (status, claim_id))

        with db.transaction():
            db.execute("INSERT INTO ...")
            db.execute("UPDATE ...")
    """

    _pool: Optional[pool.ThreadedConnectionPool] = None

    def __init__(self):
        self._ensure_pool()

    @classmethod
    def _ensure_pool(cls) -> None:
        if cls._pool is None:
            settings = get_settings()
            try:
                cls._pool = pool.ThreadedConnectionPool(
                    minconn=1,
                    maxconn=settings.db_pool_size,
                    dsn=settings.database_url,
                )
                logger.info("Database pool created", pool_size=settings.db_pool_size)
            except psycopg2.Error as e:
                logger.error("Failed to create database pool", error=str(e))
                raise DatabaseError(message="Failed to connect to database", cause=e)

    @contextmanager
    def _get_connection(self) -> Generator:
        conn = None
        try:
            conn = self._pool.getconn()
            yield conn
        finally:
            if conn:
                self._pool.putconn(conn)

    def fetch_all(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        start = time.perf_counter()
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                try:
                    cur.execute(query, params)
                    rows = cur.fetchall()
                    if cur.description and cur.rowcount and cur.rowcount > 0:
                        trimmed = query.strip().upper()
                        if trimmed.startswith(("INSERT", "UPDATE", "DELETE")):
                            conn.commit()
                    duration = (time.perf_counter() - start) * 1000
                    logger.debug("Query executed", query=query[:100], rows=len(rows), duration_ms=round(duration, 2))
                    return [dict(row) for row in rows]
                except psycopg2.Error as e:
                    logger.error("Query failed", query=query[:100], error=str(e))
                    raise DatabaseError(message=str(e), cause=e)

    def fetch_one(self, query: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        rows = self.fetch_all(query, params)
        return rows[0] if rows else None

    def execute(self, query: str, params: Optional[tuple] = None, returning: bool = False) -> Optional[Dict[str, Any]]:
        start = time.perf_counter()
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                try:
                    cur.execute(query, params)
                    result = None
                    if returning:
                        row = cur.fetchone()
                        result = dict(row) if row else None
                    conn.commit()
                    duration = (time.perf_counter() - start) * 1000
                    logger.debug("Query executed", query=query[:100], affected=cur.rowcount, duration_ms=round(duration, 2))
                    return result
                except psycopg2.Error as e:
                    conn.rollback()
                    logger.error("Query failed", query=query[:100], error=str(e))
                    raise DatabaseError(message=str(e), cause=e)

    @contextmanager
    def transaction(self) -> Generator:
        with self._get_connection() as conn:
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise

    def close(self) -> None:
        if self._pool:
            self._pool.closeall()
            logger.info("Database pool closed")


_db_instance: Optional[DatabaseConnection] = None


def get_db() -> DatabaseConnection:
    """Get singleton database connection instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseConnection()
    return _db_instance
