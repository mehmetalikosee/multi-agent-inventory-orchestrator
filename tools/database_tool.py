"""SQLite-backed DatabaseTool simulating ERP read/write operations."""

import json
import logging
import sqlite3
from pathlib import Path
from typing import Any, Optional

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from config import get_settings

logger = logging.getLogger(__name__)


class DatabaseQueryInput(BaseModel):
    """Input schema for database query (read)."""

    query: str = Field(description="SQL SELECT query to run against the ERP database")
    params: Optional[list[Any]] = Field(
        default=None,
        description="Optional list of parameters for parameterized query",
    )


class DatabaseExecuteInput(BaseModel):
    """Input schema for database execute (write)."""

    statement: str = Field(
        description="SQL statement to execute (INSERT, UPDATE, DELETE, etc.)"
    )
    params: Optional[list[Any]] = Field(
        default=None,
        description="Optional list of parameters for parameterized statement",
    )


class DatabaseTool(BaseTool):
    """
    Tool to read from and write to a local SQLite database simulating ERP.
    Use query for SELECT and execute for INSERT/UPDATE/DELETE.
    """

    name: str = "erp_database"
    description: str = (
        "Read or write to the ERP (SQLite) database. "
        "Use 'query' for SELECT (read) and 'execute' for INSERT/UPDATE/DELETE (write). "
        "Input must be JSON: for query use {\"query\": \"SELECT ...\", \"params\": []}; "
        "for execute use {\"statement\": \"UPDATE ...\", \"params\": []}."
    )
    db_path: Optional[Path] = None

    def __init__(self, db_path: Optional[Path | str] = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if db_path is None:
            settings = get_settings()
            self.db_path = settings.get_erp_path()
        else:
            self.db_path = Path(db_path)
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        """Create ERP-like tables if they do not exist."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sku TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    stock_quantity INTEGER NOT NULL DEFAULT 0,
                    min_stock_level INTEGER NOT NULL DEFAULT 10,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS inventory_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    note TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                );
                CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);
                CREATE INDEX IF NOT EXISTS idx_inventory_logs_product ON inventory_logs(product_id);
            """)
            conn.commit()
            conn.close()
            logger.info("ERP schema ensured at %s", self.db_path)
        except Exception as e:
            logger.exception("Failed to ensure ERP schema: %s", e)
            raise

    def _run(
        self,
        query_or_json: str,
        *,
        params: Optional[list[Any]] = None,
    ) -> str:
        """
        Run a read query or a write statement. If input looks like JSON with
        'query' key, run as SELECT; if 'statement' key, run as execute.
        """
        try:
            stripped = query_or_json.strip()
            if stripped.startswith("{"):
                data = json.loads(stripped)
                if "query" in data:
                    return self._run_query(
                        data["query"],
                        data.get("params"),
                    )
                if "statement" in data:
                    return self._run_execute(
                        data["statement"],
                        data.get("params"),
                    )
            # Fallback: treat as SELECT query
            return self._run_query(query_or_json, params)
        except json.JSONDecodeError as e:
            logger.warning("DatabaseTool received non-JSON input: %s", e)
            return self._run_query(query_or_json, params)
        except Exception as e:
            logger.exception("DatabaseTool error: %s", e)
            return f"Error: {e!s}"

    def _run_query(self, query: str, params: Optional[list[Any]] = None) -> str:
        """Execute a SELECT query and return results as JSON string."""
        if not query.strip().upper().startswith("SELECT"):
            return "Error: Only SELECT queries are allowed in query mode. Use execute for writes."
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params or [])
            rows = cursor.fetchall()
            result = [dict(zip(row.keys(), row)) for row in rows]
            conn.close()
            return json.dumps(result, default=str)
        except sqlite3.Error as e:
            logger.exception("Database query failed: %s", e)
            return f"Query error: {e!s}"

    def _run_execute(
        self,
        statement: str,
        params: Optional[list[Any]] = None,
    ) -> str:
        """Execute an INSERT/UPDATE/DELETE and return rowcount and message."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute(statement, params or [])
            conn.commit()
            count = cursor.rowcount
            conn.close()
            return json.dumps({"rowcount": count, "status": "ok"})
        except sqlite3.Error as e:
            logger.exception("Database execute failed: %s", e)
            return f"Execute error: {e!s}"

    async def _arun(self, query_or_json: str, **kwargs: Any) -> str:
        """Async not implemented; delegate to sync."""
        return self._run(query_or_json, **kwargs)
