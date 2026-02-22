"""CrewAI Agent and Task definitions for the Autonomous Business Logic Orchestrator."""

import logging
from typing import Any, Optional

from crewai import Agent, Crew, Process, Task

from config.prompts import (
    ANALYST_BACKSTORY,
    ANALYST_GOAL,
    ANALYST_ROLE,
    STRATEGIST_BACKSTORY,
    STRATEGIST_GOAL,
    STRATEGIST_ROLE,
    EXECUTION_OFFICER_BACKSTORY,
    EXECUTION_OFFICER_GOAL,
    EXECUTION_OFFICER_ROLE,
    TASK_ANALYZE_DESCRIPTION,
    TASK_ANALYZE_OUTPUT,
    TASK_STRATEGIZE_DESCRIPTION,
    TASK_STRATEGIZE_OUTPUT,
    TASK_EXECUTE_DESCRIPTION,
    TASK_EXECUTE_OUTPUT,
)
from tools import DatabaseTool, SupplierCommunicationTool, CompetitorScraperTool
from tools.crewai_wrappers import (
    ERPDatabaseTool,
    SupplierCommunicationCrewTool,
    CompetitorScraperCrewTool,
)

logger = logging.getLogger(__name__)


def create_analyst_agent(
    llm: Any,
    db_tool: Any = None,
    competitor_tool: Any = None,
    verbose: bool = True,
) -> Agent:
    """Build the Inventory & Market Analyst agent. Uses CrewAI-wrapped tools."""
    return Agent(
        role=ANALYST_ROLE,
        goal=ANALYST_GOAL,
        backstory=ANALYST_BACKSTORY,
        llm=llm,
        tools=[db_tool or ERPDatabaseTool(), competitor_tool or CompetitorScraperCrewTool()],
        verbose=verbose,
        allow_delegation=False,
    )


def create_strategist_agent(llm: Any, verbose: bool = True) -> Agent:
    """Build the Business Strategist agent (no tools; uses context only)."""
    return Agent(
        role=STRATEGIST_ROLE,
        goal=STRATEGIST_GOAL,
        backstory=STRATEGIST_BACKSTORY,
        llm=llm,
        tools=[],
        verbose=verbose,
        allow_delegation=False,
    )


def create_execution_officer_agent(
    llm: Any,
    db_tool: Any = None,
    supplier_tool: Any = None,
    verbose: bool = True,
) -> Agent:
    """Build the Execution Officer agent. Uses CrewAI-wrapped tools."""
    return Agent(
        role=EXECUTION_OFFICER_ROLE,
        goal=EXECUTION_OFFICER_GOAL,
        backstory=EXECUTION_OFFICER_BACKSTORY,
        llm=llm,
        tools=[db_tool or ERPDatabaseTool(), supplier_tool or SupplierCommunicationCrewTool()],
        verbose=verbose,
        allow_delegation=False,
    )


def create_analyze_task(agent: Agent) -> Task:
    """Task: Analyze inventory and competitor pricing."""
    return Task(
        name="analyze_inventory_and_market",
        description=TASK_ANALYZE_DESCRIPTION,
        expected_output=TASK_ANALYZE_OUTPUT,
        agent=agent,
    )


def create_strategize_task(agent: Agent, context_task: Task) -> Task:
    """Task: Decide reorder vs discount campaign from analyst report."""
    return Task(
        name="strategize_actions",
        description=TASK_STRATEGIZE_DESCRIPTION,
        expected_output=TASK_STRATEGIZE_OUTPUT,
        agent=agent,
        context=[context_task],
    )


def create_execute_task(agent: Agent, context_task: Task) -> Task:
    """Task: Execute supplier emails and price updates."""
    return Task(
        name="execute_actions",
        description=TASK_EXECUTE_DESCRIPTION,
        expected_output=TASK_EXECUTE_OUTPUT,
        agent=agent,
        context=[context_task],
    )


def create_crew(
    llm: Any,
    *,
    db_tool: Optional[Any] = None,
    supplier_tool: Optional[Any] = None,
    competitor_tool: Optional[Any] = None,
    verbose: bool = True,
) -> Crew:
    """
    Assemble agents and tasks into a sequential Crew. Uses CrewAI-wrapped tools (optional LangChain instances ignored for agent tools).
    """
    analyst = create_analyst_agent(llm, db_tool=db_tool, competitor_tool=competitor_tool, verbose=verbose)
    strategist = create_strategist_agent(llm, verbose=verbose)
    execution_officer = create_execution_officer_agent(
        llm, db_tool=db_tool, supplier_tool=supplier_tool, verbose=verbose
    )

    task_analyze = create_analyze_task(analyst)
    task_strategize = create_strategize_task(strategist, task_analyze)
    task_execute = create_execute_task(execution_officer, task_strategize)

    crew = Crew(
        agents=[analyst, strategist, execution_officer],
        tasks=[task_analyze, task_strategize, task_execute],
        process=Process.sequential,
        verbose=verbose,
    )
    logger.info("Crew created with 3 agents and 3 sequential tasks")
    return crew
