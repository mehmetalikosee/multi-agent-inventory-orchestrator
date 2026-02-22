"""Simulated competitor price scraping tool."""

import json
import logging
import random
from typing import Any, Optional

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Simulated competitor catalog: product name/identifier -> list of competitor prices
_MOCK_COMPETITOR_PRICES: dict[str, list[float]] = {
    "widget_a": [29.99, 31.50, 27.00],
    "widget_b": [45.00, 44.99, 48.00],
    "gadget_x": [99.99, 95.00, 102.00],
    "gadget_y": [15.99, 14.50, 16.00],
    "default": [10.00, 12.00, 11.50],
}


class CompetitorScraperInput(BaseModel):
    """Input for competitor price lookup."""

    product_identifier: str = Field(
        description="Product name, SKU, or key (e.g. widget_a, gadget_x)"
    )
    competitor_count: Optional[int] = Field(
        default=3,
        description="Max number of competitor prices to return (simulated)",
    )


class CompetitorScraperTool(BaseTool):
    """
    Simulates web scraping of competitor price points. Returns mock prices
    for a given product identifier. In production, replace with real scraping or API.
    """

    name: str = "competitor_scraper"
    description: str = (
        "Get competitor prices for a product. Input: product_identifier (e.g. widget_a, "
        "gadget_x, or product name). Returns simulated competitor prices. "
        "Use to compare our prices against the market."
    )

    def _run(self, raw_input: str, **kwargs: Any) -> str:
        """Return simulated competitor prices. Parses product_identifier from raw_input."""
        product_identifier, competitor_count = self._parse_input(raw_input)
        return self._scrape(product_identifier, competitor_count)

    def _scrape(self, product_identifier: str, competitor_count: int = 3) -> str:
        key = product_identifier.strip().lower().replace(" ", "_")
        if key not in _MOCK_COMPETITOR_PRICES:
            # Generate deterministic-ish mock prices for unknown products
            rng = random.Random(key)
            prices = [round(rng.uniform(5.0, 150.0), 2) for _ in range(competitor_count)]
        else:
            prices = _MOCK_COMPETITOR_PRICES[key][:competitor_count]
        result = {
            "product_identifier": product_identifier,
            "competitor_prices": prices,
            "min_price": min(prices),
            "max_price": max(prices),
            "note": "Simulated competitor data for demo.",
        }
        logger.info("CompetitorScraper returned %s for %s", result, product_identifier)
        return json.dumps(result)

    def _parse_input(self, raw: str) -> tuple[str, int]:
        """Parse JSON or plain product name."""
        raw = raw.strip()
        if raw.startswith("{"):
            try:
                data = json.loads(raw)
                return (
                    data.get("product_identifier", raw),
                    int(data.get("competitor_count", 3)),
                )
            except json.JSONDecodeError:
                pass
        return raw, 3

    def invoke(self, input: str | dict[str, Any], **kwargs: Any) -> str:
        """Handle string or dict input."""
        if isinstance(input, dict):
            return self._scrape(
                input.get("product_identifier", ""),
                int(input.get("competitor_count", 3)),
            )
        product_id, count = self._parse_input(input)
        return self._scrape(product_id, count)

    async def _arun(self, *args: Any, **kwargs: Any) -> str:
        """Async: delegate to sync."""
        return self._run(*args, **kwargs)
