# Simple Tool-Using Agent Loop

This example extends the baseline pipeline chatbot into a minimal **agent**.

## Ingredients

- **State**: `AgentState` with
  - `user_question`
  - `tool_calls`: list of previous calculator calls and results.
- **Tool**: `safe_calculate(expression: str) -> float`
  - Safely evaluates simple arithmetic expressions.
- **Policy**: LLM that receives the current state and returns a JSON object:

  ```json
  {
    "action": "answer" | "use_calculator",
    "expression": "...",  // when using calculator
    "answer": "..."       // when answering directly
  }
  ```

- **Control Loop**:
  - Initialize `AgentState` from the user question.
  - For up to `max_steps`:
    - Call `policy_step` to get a decision.
    - If `action == "answer"`: print and stop.
    - If `action == "use_calculator"`:
      - Call `safe_calculate(expression)`.
      - Append the tool call + result to `state.tool_calls`.
      - Continue the loop so the policy can use the new information.

## Why this is an Agent

Compared to the baseline pipeline chatbot:

- There is an explicit **policy** that chooses between actions.
- There is explicit **state** that accumulates tool calls and results.
- There is a **control loop** that can perform multiple tool calls before
  producing a final answer.

This is a minimal but complete example of an agent with a single tool.
