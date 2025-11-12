# Agentic AI Projects (Udacity MSAI)

This repository collects my work for the Udacity *Master of Science in Artificial Intelligence* “Agentic AI” track. Each sub-project explores a different flavor of agent-based workflows, retrieval systems, and LLM tooling. Everything runs locally with Python 3.11+ and is organized per project so you can dive into any build independently.

## Projects Overview

### 1. Multi-Agent Orchestrator Logistics System (`multi-agent_orchestrator_logistics_system`)
- **Goal:** Automate inventory, quoting, and fulfillment for Beaver’s Choice Paper Company using ≤5 cooperating agents.
- **Highlights:** `pydantic-ai` multi-agent graph, SQLite transactional tools, structured outputs, Vocareum OpenAI proxy integration, workflow diagram + evaluation harness.
- **Technologies:** Pydantic AI, Python, SQLite/SQLAlchemy, Pandas, Pillow (diagramming), OpenAI API (Voc proxy).

### 2. AI-Powered Genetic Workflow for Product Management (`AI-powered_genetic_workflow_for_product_mgmt`)
- **Goal:** Build agent-driven product requirement analysis with persona-specific prompting, action planning, routing, and evaluation stages.
- **Highlights:** Modular agents (direct, persona, RAG, routing), chunked knowledge CSVs, phase 1 + phase 2 workflows, documentation of the implementation pipeline.
- **Technologies:** Python, OpenAI API, custom agent harness, retrieval-augmented generation, CSV-based knowledge stores.

### 3. AI Research Agent – Video Game Industry (`AI_research_agent_video_game_industry`)
- **Goal:** Research assistant that mines structured JSON “game” data and ChromaDB embeddings to answer executive questions about the video game market.
- **Highlights:** RAG pipeline, ChromaDB vector stores, multi-step reasoning notebooks (`Udaplay_01/02`), streaming outputs to `output.txt`.
- **Technologies:** Python, ChromaDB/SQLite, OpenAI API, notebooks, retrieval + summarization agents.

### 4. Multi-Agent Travel Assistant System (`multi-agent_travel_assistant_system`)
- **Goal:** Prototype travel concierge that coordinates itinerary planning, booking decisions, and customer messaging via specialized agents.
- **Highlights:** Modular project starter (agents + tools), reusable orchestration patterns, emphasis on tool-first multi-agent design.
- **Technologies:** Python, multi-agent orchestration (framework-agnostic starter), OpenAI-compatible models.

## How to Work with the Repo

1. Clone and enter the repo:
   ```bash
   git clone https://github.com/ohara124c41/agentic_ai.git
   cd agentic_ai
   ```
2. Each project folder includes its own `README` plus scripts/notebooks. Follow those instructions to set up dependencies (often `pip install -r requirements.txt`) and run evaluations.
3. Vocareum OpenAI keys are required for agent runs—copy them into the relevant `.env` files before executing any scripts.

Feel free to explore any project independently; issues and enhancements can be tracked project-by-project using standard Git workflows.
