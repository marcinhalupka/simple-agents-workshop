from __future__ import annotations

import ast
import operator as op
from typing import Any

# Supported operators for safe evaluation
_ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
    ast.USub: op.neg,
}


def _eval_node(node: ast.AST) -> Any:
    if isinstance(node, ast.Num):  # type: ignore[attr-defined]
        return node.n
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return _ALLOWED_OPERATORS[ast.USub](_eval_node(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPERATORS:
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        return _ALLOWED_OPERATORS[type(node.op)](left, right)
    raise ValueError("Unsupported expression")


def safe_calculate(expression: str) -> float:
    """Safely evaluate a simple arithmetic expression.

    Supports +, -, *, /, **, %, parentheses, and unary minus.
    Raises ValueError for unsupported syntax.
    """
    try:
        parsed = ast.parse(expression, mode="eval")
        return float(_eval_node(parsed.body))  # type: ignore[arg-type]
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"Invalid expression: {expression}") from exc
