# Agents Workshop Repo

This repository is a small, self-contained **learning playground** for
ML/DS engineers who want to move from basic LLM pipelines to simple **agentic
systems** and then to **LangGraph**.

It is intentionally minimal and opinionated: the goal is to be easy to read
and fork, not to be production-grade.

---

## What You Will Learn

- **Pipelines vs Agents**
  - How a classic, feed-forward LLM pipeline differs from an agent.
  - When an agent is overkill vs. when it is justified.
- **Single-Tool Agents**
  - Designing a state, a policy (LLM), tools, and a control loop.
- **Router Agents**
  - Using an LLM to choose between different skills/routes.
- **LangGraph Basics**
  - Mapping a manual agent loop into a graph of nodes and edges.
  - Generating and using a Mermaid diagram for the graph.

All examples use **Python** and, by default, **OpenAI** models.

---

## Repository Structure

```text
src/
  llm_providers/
    openai_client.py        # Thin wrapper around OpenAI chat API
  pipelines/
    basic_chat.py           # Baseline non-agentic pipeline chatbot
  tools/
    calculator.py           # Safe arithmetic calculator tool
  agents/
    simple_tool_agent.py    # Single-tool agent with a control loop
    router_agent.py         # Router agent choosing chat/math/research
  langgraph_examples/
    simple_tool_agent_graph.py  # LangGraph version of simple_tool_agent

artifacts/
  00_concepts_pipelines_vs_agents.md
  01_simple_agent_loop.md
  02_router_agent_pattern.md
  03_langgraph_simple_agent_mapping.md
  04_simple_tool_agent_graph_mermaid.md
  ... (more notes as the workshop evolves)

requirements.txt
README.md
```

The `artifacts/` folder acts as a lightweight **handbook** that explains the
patterns and design decisions behind the code.

---

## Setup

1. Create and activate a virtual environment (optional but recommended):

   ```bash
   python -m venv agents
   # On PowerShell (Windows):
   .\agents\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set your OpenAI API key (example for PowerShell):

   ```powershell
   $env:OPENAI_API_KEY = "sk-..."
   # Optional: choose a model
   $env:OPENAI_MODEL = "gpt-4o-mini"
   ```

---

## Running the Examples

### 1. Baseline Pipeline Chatbot

A non-agentic, feed-forward chat pipeline.

```bash
python -m src.pipelines.basic_chat
```

Type messages; type `exit` to quit.

---

### 2. Simple Tool-Using Agent

An agent that can decide whether to use a calculator tool or answer directly.

```bash
python -m src.agents.simple_tool_agent
```

Try both chatty questions and arithmetic questions (e.g. `What is (10 + 5) * 3?`).

---

### 3. Router Agent

A router that chooses between `chat`, `math`, and `research` routes.

```bash
python -m src.agents.router_agent
```

Look at the `[route=...]` prefix in the output to see which path it picked.

---

### 4. LangGraph Simple Tool Agent

A LangGraph implementation of the simple tool-using agent.

```bash
python -m src.langgraph_examples.simple_tool_agent_graph
```

The behavior should be similar to `simple_tool_agent`, but the control flow is
expressed as a graph of nodes and edges.

---

## Visualizing the LangGraph

You can generate a **Mermaid** diagram of the simple tool agent graph with:

```bash
python -c "from src.langgraph_examples.simple_tool_agent_graph import build_graph; app = build_graph().compile(); g = app.get_graph(); print(g.draw_mermaid())"
```

Copy the output into a Markdown file or an online Mermaid editor. An example
output is stored in:

- `artifacts/04_simple_tool_agent_graph_mermaid.md`

---

## How to Use This Repo

- **Reading order (suggested):**
  1. `artifacts/00_concepts_pipelines_vs_agents.md`
  2. `src/pipelines/basic_chat.py`
  3. `src/agents/simple_tool_agent.py` + `artifacts/01_simple_agent_loop.md`
  4. `src/agents/router_agent.py` + `artifacts/02_router_agent_pattern.md`
  5. `src/langgraph_examples/simple_tool_agent_graph.py` +
     `artifacts/03_langgraph_simple_agent_mapping.md` and
     `artifacts/04_simple_tool_agent_graph_mermaid.md`

- **As a workshop:**
  - Fork the repo.
  - Rebuild or extend each example (e.g. new tools, richer routing, more
    complex graphs).
  - Encourage participants to read the artifacts alongside the code.

This repo is intentionally small; treat it as a **starting point** for your
own agentic experiments and internal training material.
