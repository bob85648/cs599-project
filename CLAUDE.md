# CLAUDE.md

This file provides guidance to Claude Code (AI IDE) when working with code in this repository.

## Project Overview

TravelMind is a Python 3.13 multi-agent travel assistant built on the **AgentScope** framework. It uses a Plan-and-Execute architecture where an `IntentionAgent` classifies user intent via LLM, then an `OrchestrationAgent` dispatches work to 6 specialized sub-agents (Skill Plugins). The LLM is accessed via an OpenAI-compatible API endpoint (configured in `config.py`).

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the interactive CLI
python cli.py

# Run health check (non-interactive, exit code 0/1)
python cli.py health

# Initialize RAG knowledge base (first time only)
python .claude/skills/ask-question/script/init_knowledge_base.py

# Tests (standalone scripts, no test framework)
python tests/test_cli_qa.py                  # End-to-end QA integration
python tests/test_memory_system.py           # Memory system
python tests/test_intention_agent.py         # Intent recognition
python tests/test_orchestration.py           # Orchestration
python tests/test_event_collection_agent.py  # Event collection
python tests/test_information_query_agent.py # Information query
python tests/test_rag_agent.py               # RAG knowledge
```

No linter, formatter, or CI configuration exists.

## Architecture

### Data Flow

```
User Input → IntentionAgent (intent classification + agent scheduling)
          → OrchestrationAgent (priority-based parallel dispatch)
          → Sub-Agents (executed via asyncio.gather)
          → Result aggregation + memory update
```

### Core Orchestration (`agents/`)

- **`intention_agent.py`** — LLM-based semantic intent recognition. Outputs structured JSON with intents, entities, rewritten query, and an agent schedule with priorities. Supports 6 intent types: `itinerary_planning`, `memory_query`, `preference`, `rag_knowledge`, `information_query`, `event_collection`.
- **`orchestration_agent.py`** — Groups agents by priority, runs same-priority agents in parallel via `asyncio.gather`, aggregates results, updates memory.
- **`lazy_agent_registry.py`** — Scans `.claude/skills/*/script/agent.py` at init time, imports/creates agent classes on first access. Contains legacy name mappings (e.g., `rag_knowledge` → `ask-question`).

### Skill Plugins (`.claude/skills/`)

Each skill is an independent agent extending `agentscope.agent.AgentBase`. Structure per skill:

```
.claude/skills/{skill-name}/
├── SKILL.md           # YAML frontmatter (name, description, triggers) + markdown instructions
└── script/
    └── agent.py       # Agent class implementation
```

| Skill Directory | Agent Class | Purpose |
|---|---|---|
| `ask-question` | `RAGKnowledgeAgent` | RAG knowledge base Q&A via Milvus + BGE embeddings |
| `event-collection` | `EventCollectionAgent` | Extract trip details (origin, destination, dates, purpose) |
| `memory-query` | `MemoryQueryAgent` | Query historical memory (trips, preferences, chat) |
| `plan-trip` | `ItineraryPlanningAgent` | Generate complete itinerary plans |
| `preference` | `PreferenceAgent` | Manage user preferences (append/overwrite modes) |
| `query-info` | `InformationQueryAgent` | Real-time info via DuckDuckGo search + LLM summary |

### Memory System (`context/`)

- **`memory_manager.py`** — Unified facade. `add_message()` writes to both layers. `get_long_term_summary_async()` uses LLM to summarize history.
- **`short_term_memory.py`** — In-memory sliding window of last 10 turns (20 messages).
- **`long_term_memory.py`** — JSON file persistence at `data/memory/{user_id}.json`. Stores preferences, chat history, trip history, statistics.

### Utilities (`utils/`)

- **`circuit_breaker.py`** — CLOSED/OPEN/HALF_OPEN states for LLM call protection.
- **`llm_resilience.py`** — Exponential backoff retry (max 3) with jitter for timeout/429/5xx.
- **`json_parser.py`** — Robust JSON parsing handling markdown code blocks, single quotes, trailing commas, control characters.
- **`skill_loader.py`** — Reads SKILL.md YAML frontmatter for intent recognition metadata; provides `get_skill_content()` for progressive disclosure (full instructions loaded only at execution time).

### Configuration

- **`config.py`** — All configuration: `LLM_CONFIG` (API key, model, base URL), `RESILIENCE_CONFIG` (retry, circuit breaker), `RAG_CONFIG` (embedding model path).
- **`config_agentscope.py`** — AgentScope framework initialization and model config helper.

## Key Implementation Details

- All agents communicate via `agentscope.message.Msg` objects.
- The orchestrator runs sub-agents as async tasks; priority 1 agents (memory_query, event_collection, preference, information_query, rag_knowledge) run in parallel, priority 2 (itinerary_planning) runs after.
- `SkillLoader` implements Progressive Disclosure: only skill metadata (name, description, triggers) is loaded during intent recognition; full SKILL.md content is loaded on-demand when the skill is actually invoked.
- The `LazyAgentRegistry` scans `.claude/skills/*/script/agent.py` directories and uses a mapping dict in `cli.py` to translate legacy intent names to skill directory names.
- RAG knowledge base documents are stored in `.claude/skills/ask-question/data/documents/` (8 text files covering travel policies, reimbursement, FAQs, etc.). The Milvus DB is generated at `.claude/skills/ask-question/data/rag_knowledge/`.
- The BGE Chinese embedding model is stored locally at `data/models/bge-small-zh-v1.5/`.
