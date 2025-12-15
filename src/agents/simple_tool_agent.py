from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List

from src.llm_providers.openai_client import OpenAILLMClient
from src.tools.calculator import safe_calculate


SYSTEM_PROMPT = """You are a reasoning assistant that can decide whether to call a calculator tool
or answer directly. You operate in a loop. At each step, you must respond with a
single JSON object with this schema:

{
  "action": "answer" | "use_calculator",
  "expression": string | null,     # required when action == "use_calculator"
  "answer": string | null          # required when action == "answer"
}

Rules:
- When the user asks a question that requires arithmetic or numeric computation,
  prefer action = "use_calculator" and provide a concise, valid arithmetic expression
  in the "expression" field.
- When you have enough information to provide the final answer to the user,
  use action = "answer" and write your answer in natural language in the
  "answer" field.
- Do not include any explanation outside of the JSON.
- Always return syntactically valid JSON.
"""


@dataclass
class AgentState:
    user_question: str
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)


def build_client() -> OpenAILLMClient:
    return OpenAILLMClient()


def policy_step(client: OpenAILLMClient, state: AgentState) -> Dict[str, Any]:
    """One agent policy step: ask the LLM what to do next.

    We show the LLM the original question and a summary of previous tool calls.
    """
    history: List[Dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    # Provide the question and current tool-call history as context.
    context = {
        "question": state.user_question,
        "tool_calls": state.tool_calls,
    }
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
        # Fallback: treat the raw string as a direct answer.
        return {"action": "answer", "expression": None, "answer": raw}

    # Normalize keys we expect.
    action = decision.get("action")
    expression = decision.get("expression")
    answer = decision.get("answer")
    return {"action": action, "expression": expression, "answer": answer}


def run_agent_cli(max_steps: int = 4) -> None:
    client = build_client()
    print("Simple tool-using agent. Type 'exit' to quit.\n")

    while True:
        user_input = input("you> ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Exiting.")
            break
        if not user_input:
            continue

        state = AgentState(user_question=user_input)

        for step in range(max_steps):
            decision = policy_step(client, state)
            action = decision.get("action")

            if action == "answer":
                answer = decision.get("answer") or ""
                print(f"agent> {answer}\n")
                break

            if action == "use_calculator":
                expr = decision.get("expression")
                if not expr:
                    print("agent> Policy requested calculator but gave no expression.\n")
                    break
                try:
                    result = safe_calculate(expr)
                except ValueError as exc:
                    state.tool_calls.append(
                        {"tool": "calculator", "expression": expr, "error": str(exc)}
                    )
                    print(f"agent> Calculator error: {exc}\n")
                    break

                # Record successful tool call and let the agent use the result next step.
                state.tool_calls.append(
                    {"tool": "calculator", "expression": expr, "result": result}
                )
                print(f"[tool] calculator({expr}) = {result}")
                continue

            # Unknown action: bail out gracefully.
            print(f"agent> Unknown action from policy: {action}\n")
            break


if __name__ == "__main__":
    run_agent_cli()
