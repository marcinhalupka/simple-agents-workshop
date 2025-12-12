# Pipelines vs Agents: Working Definitions

## Pipeline

- **Structure**: Directed acyclic flow of steps.
- **Execution model**: One pass per request.
- **Control**: Outside the LLM; no autonomous loop.
- **Typical shape**: `input -> preprocess -> LLM call(s) -> postprocess -> output`.
- **Good for**:
  - Well-structured, predictable tasks.
  - Static tool sequences or simple conditional branching.

## Agent

- **Structure**: Loop over state + actions.
- **Execution model**: Repeated observe -> decide -> act -> update until done.
- **Control**: Often delegated to an LLM policy that chooses the next action.
- **Key ingredients**:
  - **State**: Conversation, tools used, intermediate results.
  - **Policy**: Mapping from state to next action (tool call, LLM call, stop).
  - **Tools**: External capabilities invoked by the policy.
  - **Control loop**: Glue that ties state, policy, and tools together.
- **Good for**:
  - When the sequence of actions is *not known in advance*.
  - Tasks requiring exploration, retries, or adaptive planning.

## Heuristic for Design Choices

- Start with a **pipeline** when you can write down the steps as a DAG.
- Introduce an **agent loop** when:
  - You cannot comfortably enumerate all reasonable next steps.
  - You want the system to decide *which tools/skills to use and in what order*.
  - The task benefits from iterative refinement, search, or self-critique.
