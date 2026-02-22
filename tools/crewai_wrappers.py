"""
CrewAI-compatible tool wrappers. CrewAI expects tools that inherit from crewai.tools.BaseTool;
our LangChain tools are wrapped here so agents can use them.
"""

from typing import Any

from crewai.tools import BaseTool

from tools.database_tool import DatabaseTool as LangChainDatabaseTool
from tools.supplier_communication_tool import SupplierCommunicationTool as LangChainSupplierTool
from tools.competitor_scraper_tool import CompetitorScraperTool as LangChainCompetitorTool


class ERPDatabaseTool(BaseTool):
    """CrewAI wrapper for ERP (SQLite) read/write. Pass JSON: {\"query\": \"SELECT ...\"} or {\"statement\": \"UPDATE ...\"}."""

    name: str = "erp_database"
    description: str = (
        "Read or write to the ERP (SQLite) database. "
        "Use JSON input: {\"query\": \"SELECT ...\"} for reads, {\"statement\": \"UPDATE/INSERT/DELETE ...\"} for writes."
    )

    def _run(self, query_or_json: str, **kwargs: Any) -> str:
        tool = LangChainDatabaseTool()
        return tool._run(query_or_json, **kwargs)


class SupplierCommunicationCrewTool(BaseTool):
    """CrewAI wrapper for sending supplier emails. Pass JSON: {\"to_email\": \"...\", \"subject\": \"...\", \"body\": \"...\"}."""

    name: str = "supplier_communication"
    description: str = (
        "Send an email to a supplier. Input: JSON with to_email, subject, and body. "
        "Use for reorder requests or alerts. Mock mode logs only unless SMTP is configured."
    )

    def _run(self, raw_input: str, **kwargs: Any) -> str:
        tool = LangChainSupplierTool()
        return tool._run(raw_input, **kwargs)


class CompetitorScraperCrewTool(BaseTool):
    """CrewAI wrapper for competitor prices. Pass product identifier (e.g. widget_a) or JSON {\"product_identifier\": \"...\"}."""

    name: str = "competitor_scraper"
    description: str = (
        "Get competitor prices for a product. Input: product_identifier (e.g. widget_a, gadget_x) or JSON. "
        "Returns simulated competitor prices for comparison."
    )

    def _run(self, raw_input: str, **kwargs: Any) -> str:
        tool = LangChainCompetitorTool()
        return tool._run(raw_input, **kwargs)
