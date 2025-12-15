from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List

from src.llm_providers.openai_client import OpenAILLMClient
from src.tools.calculator import safe_calculate


SYSTEM_PROMPT = """You are a routing assistant that decides how to handle a user's question.
You can choose between three routes:

- "chat": answer directly as a helpful assistant.
- "math": use a calculator tool to perform arithmetic.
- "research": pretend to do lightweight research and then answer.

You must respond with a single JSON object with this schema:

{
  "route": "chat" | "math" | "research",
  "expression": string | null,   # required when route == "math"
  "answer": string | null        # required when route == "chat" or "research"
}

Rules:
- For clearly arithmetic/numeric questions, use route = "math" and provide an
  arithmetic expression in "expression".
- For general questions that do not require external data, use route = "chat".
- For questions that sound like they require looking things up or combining
  multiple pieces of knowledge (e.g. pros/cons, comparisons), use route = "research".
- When using the "research" route in this simple example, you should just
  answer from your general knowledge; do NOT fabricate references.
- Do not include any explanation outside of the JSON.
- Always return syntactically valid JSON.
"""


@dataclass
class RouterDecision:
    route: str
    expression: str | None
    answer: str | None


def build_client() -> OpenAILLMClient:
    return OpenAILLMClient()


def router_policy(client: OpenAILLMClient, question: str) -> RouterDecision:
    history: List[Dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": "Decide route for this question and respond with JSON only:\n"
            + json.dumps({"question": question}),
        },
    ]

    raw = client.chat(history, temperature=0)

    try:
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError
    except Exception:
        # Fallback: treat as direct chat answer.
        return RouterDecision(route="chat", expression=None, answer=raw)

    route = str(data.get("route", "chat"))
    expression = data.get("expression")
    answer = data.get("answer")
    return RouterDecision(route=route, expression=expression, answer=answer)


def handle_math_route(expression: str | None) -> str:
    if not expression:
        return "Router selected math route but did not provide an expression."
    try:
        result = safe_calculate(expression)
    except ValueError as exc:
        return f"Calculator error: {exc}"
    return f"The result of {expression} is {result}."


def run_router_cli() -> None:
    client = build_client()
    print("Router agent. Type 'exit' to quit.\n")

    while True:
        user_input = input("you> ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Exiting.")
            break
        if not user_input:
            continue

        decision = router_policy(client, user_input)

        if decision.route == "math":
            response = handle_math_route(decision.expression)
            print(f"[route=math] agent> {response}\n")
            continue

        if decision.route == "research":
            # In a more advanced system, this is where we would call a
            # retrieval or web-search tool. For now we just use the LLM
            # answer that the policy produced.
            if decision.answer:
                print(f"[route=research] agent> {decision.answer}\n")
            else:
                print("[route=research] agent> (no answer produced by policy)\n")
            continue

        # Default: chat
        if decision.answer:
            print(f"[route=chat] agent> {decision.answer}\n")
        else:
            print("[route=chat] agent> (no answer produced by policy)\n")


if __name__ == "__main__":
    run_router_cli()
