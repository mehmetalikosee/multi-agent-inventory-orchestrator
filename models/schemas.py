"""Pydantic schemas for inter-agent and tool data validation."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ActionType(str, Enum):
    """Allowed strategic actions."""

    REORDER = "reorder"
    DISCOUNT_CAMPAIGN = "discount_campaign"
    NO_ACTION = "no_action"


class LowStockItem(BaseModel):
    """Single low-stock finding from analyst."""

    product_id: int = Field(description="Product ID")
    sku: str = Field(description="Product SKU")
    name: str = Field(description="Product name")
    current_stock: int = Field(description="Current quantity")
    min_stock_level: int = Field(description="Minimum safe level")


class PriceFinding(BaseModel):
    """Single price competitiveness finding."""

    product_id: int = Field(description="Product ID")
    sku: str = Field(description="Product SKU")
    our_price: float = Field(description="Our current price")
    competitor_min: float = Field(description="Lowest competitor price")
    competitor_avg: Optional[float] = Field(default=None, description="Avg competitor price")


class ProductSummary(BaseModel):
    """Minimal product info for execution."""

    product_id: int
    sku: str
    new_price: Optional[float] = None
    reorder_quantity: Optional[int] = None


class AnalystReport(BaseModel):
    """Structured output from the Inventory & Market Analyst."""

    low_stock_items: list[LowStockItem] = Field(default_factory=list)
    uncompetitive_prices: list[PriceFinding] = Field(default_factory=list)
    summary: str = Field(default="", description="Short narrative summary")


class StrategistDecision(BaseModel):
    """Single decision from the Business Strategist."""

    finding_ref: str = Field(description="Reference to finding (e.g. SKU or short id)")
    action: ActionType = Field(description="Chosen action")
    justification: str = Field(default="", description="Brief justification")


class ExecutionResult(BaseModel):
    """Result of execution phase (emails sent, prices updated)."""

    emails_sent: list[str] = Field(default_factory=list, description="List of 'to_email' sent")
    prices_updated: list[dict] = Field(
        default_factory=list,
        description="List of {sku, old_price, new_price}",
    )
    errors: list[str] = Field(default_factory=list)
