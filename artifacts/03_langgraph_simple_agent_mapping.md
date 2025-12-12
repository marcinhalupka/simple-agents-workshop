# LangGraph Mapping of the Simple Tool Agent

This example rewrites the manual `simple_tool_agent` using **LangGraph**.

## Manual Agent (Recap)

Key pieces in `simple_tool_agent.py`:

- `AgentState(question, tool_calls)` tracks the question and calculator calls.
- `policy_step` (LLM) decides `{action, expression, answer}`.
- Loop:
  - If `action == "answer"` -> print and stop.
  - If `action == "use_calculator"` -> call `safe_calculate`, update `tool_calls`,
    then ask the policy again.

## LangGraph Version

In `src/langgraph_examples/simple_tool_agent_graph.py` we define:

- **State**: `GraphState` with fields:
  - `question: str`
  - `tool_calls: list`
  - `action: "answer" | "use_calculator" | None`
  - `expression: str | None`
  - `answer: str | None`

- **Nodes**:
  - `policy_node(state)`
    - Calls the LLM with `question` and `tool_calls`.
    - Parses the JSON decision and updates `state.action`, `state.expression`,
      and `state.answer`.
  - `calculator_node(state)`
    - Uses `safe_calculate(expression)`.
    - Appends the tool call + result to `state.tool_calls`.

- **Router**:

  ```python
  def router(state: GraphState) -> str:
      if state.action == "answer":
          return END
      if state.action == "use_calculator":
          return "calculator"
      return END
  ```

- **Graph wiring**:

  ```python
  graph = StateGraph(GraphState)
  graph.add_node("policy", policy_node)
  graph.add_node("calculator", calculator_node)

  graph.set_entry_point("policy")
  graph.add_conditional_edges("policy", router, {"calculator": "calculator", END: END})
  graph.add_edge("calculator", "policy")
  ```

This structure mirrors the manual control flow, but the transitions are now
explicit in the graph instead of being hand-coded in a `for` loop.

## How to Run

From the project root after installing `langgraph` and `langchain-core`:

```bash
python -m src.langgraph_examples.simple_tool_agent_graph
```

Then try questions that require arithmetic vs pure chat. Behavior should be
similar to the manual `simple_tool_agent`, but the control flow is now
expressed as a graph of nodes and edges.
