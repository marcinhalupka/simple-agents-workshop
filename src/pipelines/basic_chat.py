from __future__ import annotations

import os
from src.llm_providers.openai_client import OpenAILLMClient


SYSTEM_PROMPT = """You are a concise, helpful assistant for interactive experiments
with LLM pipelines and agents. Answer clearly and avoid unnecessary verbosity.
"""


def build_client() -> OpenAILLMClient:
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    return OpenAILLMClient(model=model)


def run_cli_chat() -> None:
    client = build_client()
    print("Baseline pipeline chat. Type 'exit' to quit.\n")

    history = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    while True:
        user_input = input("you> ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Exiting.")
            break
        if not user_input:
            continue

        history.append({"role": "user", "content": user_input})
        # Pipeline behavior: one call per turn, no tool loop, no dynamic control flow.
        assistant_reply = client.chat(history)
        history.append({"role": "assistant", "content": assistant_reply})

        print(f"agent> {assistant_reply}\n")


if __name__ == "__main__":
    run_cli_chat()
