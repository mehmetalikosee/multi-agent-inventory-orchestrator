"""
Quick test script: runs tool and config checks without calling the LLM.
Run: python run_tests.py
"""

import json
import sys
from pathlib import Path

# Project root on path
_root = Path(__file__).resolve().parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

def test_config():
    """Load settings and check OpenAI key is set (if provider is openai)."""
    from config import get_settings
    s = get_settings()
    assert s.llm_provider in ("openai", "anthropic"), "Invalid LLM_PROVIDER"
    if s.llm_provider == "openai":
        assert s.openai_api_key and s.openai_api_key.startswith("sk-"), "Set OPENAI_API_KEY in .env"
    print("  config: OK")

def test_database_tool():
    """DatabaseTool: create DB, query products, run an update."""
    from tools import DatabaseTool
    db = DatabaseTool()
    # Read
    out = db._run('{"query": "SELECT id, sku, name, price, stock_quantity FROM products LIMIT 2"}')
    data = json.loads(out)
    assert isinstance(data, list), "Query should return a list"
    print("  database_tool (query): OK")
    # Write (safe update that doesn't break demo)
    out = db._run('{"statement": "UPDATE products SET updated_at = CURRENT_TIMESTAMP WHERE id = 1", "params": []}')
    result = json.loads(out)
    assert result.get("status") == "ok", "Execute should return status ok"
    print("  database_tool (execute): OK")

def test_competitor_scraper_tool():
    """CompetitorScraperTool: get mock prices for a product."""
    from tools import CompetitorScraperTool
    tool = CompetitorScraperTool()
    out = tool._run("widget_a")
    data = json.loads(out)
    assert "competitor_prices" in data and "min_price" in data
    print("  competitor_scraper_tool: OK")

def test_supplier_communication_tool():
    """SupplierCommunicationTool: mock send (no real email)."""
    from tools import SupplierCommunicationTool
    tool = SupplierCommunicationTool()
    out = tool._run('{"to_email": "supplier@test.com", "subject": "Reorder", "body": "Please reorder 100 units"}')
    assert "mock_sent" in out or "sent" in out or "status" in out
    print("  supplier_communication_tool: OK")

def test_models():
    """Pydantic models validate."""
    from models import AnalystReport, StrategistDecision, ActionType
    r = AnalystReport(summary="Test", low_stock_items=[], uncompetitive_prices=[])
    assert r.summary == "Test"
    d = StrategistDecision(finding_ref="SKU-1", action=ActionType.REORDER, justification="Low stock")
    assert d.action == ActionType.REORDER
    print("  models: OK")

def main():
    print("Running quick tests (no LLM calls)...\n")
    try:
        test_config()
        test_database_tool()
        test_competitor_scraper_tool()
        test_supplier_communication_tool()
        test_models()
        print("\nAll checks passed. Run the full flow with: python main.py")
        return 0
    except Exception as e:
        print(f"\nFAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
