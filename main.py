"""
Entry point for the Autonomous Business Logic Orchestrator.

Runs the CrewAI flow: Analyst -> Strategist -> Execution Officer.
"""

import logging
import sys
from pathlib import Path

# Ensure project root is on path
_project_root = Path(__file__).resolve().parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from dotenv import load_dotenv

load_dotenv()

from config import get_settings
from agents import create_crew
from tools import DatabaseTool

# ----- Logging setup -----
def setup_logging(level: str = "INFO") -> None:
    """Configure root logger with a clear format."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )


def seed_erp_if_empty(db_tool: DatabaseTool) -> None:
    """Insert sample products if the ERP has no data (for demo)."""
    import sqlite3
    path = db_tool.db_path
    if path is None:
        return
    try:
        conn = sqlite3.connect(str(path))
        cur = conn.execute("SELECT COUNT(*) FROM products")
        if cur.fetchone()[0] == 0:
            conn.executescript("""
                INSERT INTO products (sku, name, price, stock_quantity, min_stock_level)
                VALUES
                    ('widget_a', 'Widget A', 32.99, 5, 15),
                    ('widget_b', 'Widget B', 46.50, 50, 20),
                    ('gadget_x', 'Gadget X', 98.00, 3, 10),
                    ('gadget_y', 'Gadget Y', 15.50, 25, 15);
            """)
            conn.commit()
            logging.getLogger(__name__).info("Seeded ERP with sample products")
        conn.close()
    except Exception as e:
        logging.getLogger(__name__).warning("Could not seed ERP: %s", e)


def get_llm():
    """Return the configured LangChain LLM (OpenAI or Anthropic)."""
    from langchain_openai import ChatOpenAI
    from langchain_anthropic import ChatAnthropic

    settings = get_settings()
    if settings.llm_provider == "anthropic":
        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required when LLM_PROVIDER=anthropic")
        return ChatAnthropic(
            model=settings.anthropic_model_name,
            api_key=settings.anthropic_api_key,
            temperature=0.2,
        )
    # Default: OpenAI
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is required when LLM_PROVIDER=openai")
    return ChatOpenAI(
        model=settings.openai_model_name,
        api_key=settings.openai_api_key,
        temperature=0.2,
    )


def run() -> None:
    """Run the orchestrator crew once."""
    settings = get_settings()
    setup_logging(settings.log_level)
    logger = logging.getLogger(__name__)

    try:
        llm = get_llm()
    except ValueError as e:
        logger.error("LLM configuration error: %s", e)
        sys.exit(1)

    db_tool = DatabaseTool()
    seed_erp_if_empty(db_tool)

    crew = create_crew(llm, verbose=True)

    logger.info("Starting crew kickoff...")
    inputs = {}  # Optional: e.g. {"focus_sku": "widget_a"}
    result = crew.kickoff(inputs=inputs)
    logger.info("Crew finished. Result: %s", result)


if __name__ == "__main__":
    run()
