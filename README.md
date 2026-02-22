# Autonomous Business Logic Orchestrator

A production-ready **multi-agent system** built with **CrewAI**, **LangChain**, and **Pydantic**. Agents analyze ERP-style inventory and competitor data, decide on reorders and discount campaigns, and execute supplier communications and price updates.

## Architecture

- **Framework:** CrewAI (agent orchestration, sequential process)
- **LLM:** LangChain (OpenAI GPT-4o or Anthropic Claude 3.5 Sonnet)
- **Memory/Vector:** Pinecone (RAG stub; ready for business documents)
- **Validation:** Pydantic models for inter-agent data

### Agents

| Agent | Role | Tools | Responsibility |
|-------|------|--------|-----------------|
| **Inventory & Market Analyst** | Monitors ERP and competitor pricing | DatabaseTool, CompetitorScraperTool | Identify low stock and uncompetitive prices |
| **Business Strategist** | Evaluates reports vs ROI goals | — | Decide reorder vs discount campaign |
| **Execution Officer** | Interfaces with external APIs | DatabaseTool, SupplierCommunicationTool | Send supplier emails, update product prices |

### Custom Tools (LangChain)

- **DatabaseTool** – Read/write SQLite (simulated ERP): `products`, `inventory_logs`
- **SupplierCommunicationTool** – Send emails to suppliers (mock SMTP or real)
- **CompetitorScraperTool** – Simulated competitor price lookup

## File Structure

```
.
├── main.py                 # Entry point; runs the crew
├── agents.py              # CrewAI Agent and Task definitions
├── config/
│   ├── __init__.py
│   ├── settings.py        # Pydantic Settings (env)
│   ├── prompts.py         # Agent roles and task copy
│   └── pinecone_rag.py    # Pinecone RAG stub
├── tools/
│   ├── __init__.py
│   ├── database_tool.py
│   ├── supplier_communication_tool.py
│   └── competitor_scraper_tool.py
├── models/
│   ├── __init__.py
│   └── schemas.py         # Pydantic models for agents
├── .env.example
└── requirements.txt
```

## Setup

1. **Clone the repository** (or download and extract the project).

2. **Install dependencies** (use the same Python that runs `main.py`)

   From the project folder (after cloning the repo):

   ```powershell
   cd path/to/autonomous-business-logic-orchestrator
   python -m pip install -r requirements.txt
   ```

   If you use the Windows Store Python 3.13 explicitly:

   ```powershell
   & "C:/Users/memet/AppData/Local/Microsoft/WindowsApps/python3.13.exe" -m pip install -r requirements.txt
   ```

   **If you see `ModuleNotFoundError: No module named 'crewai'`** — dependencies are not installed for that Python. Run one of the commands above and wait for it to finish (can take 2–5 minutes). Then run `python main.py` again.

   Optional: use a virtual environment so the project has its own packages:

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python main.py
   ```

3. **Environment**

   Copy `.env.example` to `.env` and set at least:

   - `OPENAI_API_KEY` (if using OpenAI), or
   - `ANTHROPIC_API_KEY` and `LLM_PROVIDER=anthropic` (if using Anthropic)
   - Optionally: Pinecone keys, SMTP settings (see `.env.example`)

4. **Run**

   ```bash
   python main.py
   ```

   The crew runs sequentially: **Analyze → Strategize → Execute**. The ERP DB is created under `./data/erp.db` and seeded with sample products if empty.

Before production, see **[PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)**.

## How to test

**1. Quick checks (no API calls)** – tools and config only:

```bash
python run_tests.py
```

This verifies: config/env, DatabaseTool read/write, CompetitorScraperTool, SupplierCommunicationTool (mock), and Pydantic models.

**2. Full flow (uses OpenAI/Anthropic)** – run the whole crew:

```bash
python main.py
```

Ensure `.env` has `OPENAI_API_KEY` (or Anthropic key and `LLM_PROVIDER=anthropic`). The crew will analyze inventory, decide actions, and execute (emails are mock-logged unless you configure real SMTP).

**3. Optional: pytest** – add `pytest` and run:

```bash
pip install pytest
pytest tests/ -v
```

(See `tests/` for unit tests if added.)

## Configuration

- **LLM:** `LLM_PROVIDER=openai` or `anthropic`; set the corresponding API key and model name in `.env`.
- **ERP:** `ERP_DATABASE_PATH` (default `./data/erp.db`).
- **SMTP:** Set `SMTP_MOCK_MODE=false` and SMTP_* variables to send real emails; otherwise emails are only logged.
- **Pinecone:** Optional; configure for RAG over business documents (see `config/pinecone_rag.py`).

## Coding Standards

- **OOP:** Tools and config are class-based; agents/tasks built via factory functions.
- **Type hints:** Used on all public functions and tool methods.
- **Error handling:** Try/except in tools and main with logging.
- **Logging:** Structured logging for agent actions and tool calls; level via `LOG_LEVEL`.

## License

MIT License. See [LICENSE](LICENSE). Use and modify as needed for your project.
