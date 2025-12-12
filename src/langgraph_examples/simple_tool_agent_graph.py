from __future__ import annotations

import json
from typing import Any, Dict, List, Literal

from langgraph.graph import END, StateGraph

from src.llm_providers.openai_client import OpenAILLMClient
from src.tools.calculator import safe_calculate


Action = Literal["answer", "use_calculator"]


SYSTEM_PROMPT = """You are a reasoning assistant that can decide whether to call a calculator tool
or answer directly. You operate in a loop. At each step, you must respond with a
single JSON object with this schema:

{
  "action": "answer" | "use_calculator",
  "expression": string | null,
  "answer": string | null
}

- Prefer action = "use_calculator" when arithmetic is required.
- When you have enough information to answer the user's question, use
  action = "answer" and provide the final answer in natural language.
- Do not include any explanation outside of the JSON.
- Always return syntactically valid JSON.
"""


def build_client() -> OpenAILLMClient:
    return OpenAILLMClient()


def policy_node(state: Dict[str, Any], client: OpenAILLMClient | None = None) -> Dict[str, Any]:
    """Node that decides the next action based on current state."""
    if client is None:
        client = build_client()

    history: List[Dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]
    context = {"question": state["question"], "tool_calls": state["tool_calls"]}
    history.append(
        {
            "role": "user",
            "content": "Decide next action for this state:\n" + json.dumps(context),
        }
    )

    raw = client.chat(history, temperature=0)

    try:
        decision = json.loads(raw)
        if not isinstance(decision, dict):
            raise ValueError
    except Exception:
        # Fallback: treat raw as direct answer.
        state["action"] = "answer"
        state["expression"] = None
        state["answer"] = raw
        return state

    state["action"] = decision.get("action")
    state["expression"] = decision.get("expression")
    state["answer"] = decision.get("answer")
    return state


def calculator_node(state: Dict[str, Any]) -> Dict[str, Any]:
    expr = state.get("expression")
    if not expr:
        state["tool_calls"].append(
            {"tool": "calculator", "expression": expr, "error": "no expression provided"}
        )
        return state
    try:
        result = safe_calculate(expr)
    except ValueError as exc:
        state["tool_calls"].append(
            {"tool": "calculator", "expression": expr, "error": str(exc)}
        )
        return state

    state["tool_calls"].append({"tool": "calculator", "expression": expr, "result": result})
    return state


def router(state: Dict[str, Any]) -> str:
    """Routing logic between nodes based on state.action.

    This replaces the manual `if action == ...` branching in the loop.
    """
    if state.get("action") == "answer":
        return END
    if state.get("action") == "use_calculator":
        return "calculator"
    # Unknown action: treat as answer and end.
    state["answer"] = state.get("answer") or "I could not determine an action; stopping."
    return END


def build_graph() -> StateGraph:
    graph = StateGraph(dict)

    # Register nodes. We partially apply the client inside policy_node.
    graph.add_node("policy", lambda s: policy_node(s))
    graph.add_node("calculator", calculator_node)

    graph.set_entry_point("policy")
    graph.add_conditional_edges("policy", router, {"calculator": "calculator", END: END})
    graph.add_edge("calculator", "policy")

    return graph


def run_cli(max_steps: int = 5) -> None:
    graph = build_graph().compile()
    print("LangGraph simple tool agent. Type 'exit' to quit.\n")

    while True:
        user_input = input("you> ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Exiting.")
            break
        if not user_input:
            continue

        state: Dict[str, Any] = {
            "question": user_input,
            "tool_calls": [],
            "action": None,
            "expression": None,
            "answer": None,
        }
        # Run the graph until END or max_steps transitions.
        # We use the sync interface here for simplicity.
        for _ in range(max_steps):
            state = graph.invoke(state)
            if state.get("action") == "answer":
                break

        answer = state.get("answer") or "(no answer produced)"
        print(f"agent> {answer}\n")


if __name__ == "__main__":
    run_cli()
