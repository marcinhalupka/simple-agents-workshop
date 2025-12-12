# Router Agent Pattern

This example shows a simple **router agent** that chooses between different
handling modes for a user question.

## Capabilities

The router can select between three routes:

- `chat`: answer directly using the LLM.
- `math`: send the question to a calculator tool.
- `research`: pretend to perform lightweight research and respond.

The policy (an LLM) returns a JSON object like:

```json
{
  "route": "chat" | "math" | "research",
  "expression": "...",  // when route == "math"
  "answer": "..."       // when route == "chat" or "research"
}
```

## Control Flow

1. The router policy is called with the user question.
2. The LLM decides the `route` and optionally provides an `expression` or
   `answer`.
3. The top-level control function dispatches based on `route`:
   - `math` -> call `safe_calculate(expression)` and format the result.
   - `research` -> (currently) use the LLM-produced answer.
   - `chat` -> use the LLM-produced answer directly.

## Why This Matters

- This pattern is very common in practical systems: a **single front-door
  agent** that picks which skill or subsystem should handle the request.
- It keeps each skill focused while centralizing high-level decision-making.
- Later, this maps naturally to LangGraph as a node that branches to other
  nodes based on the `route`.
