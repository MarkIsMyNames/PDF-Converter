"""Enforce that no magic string or numeric literals appear in source module function bodies.

Any raw string or number that belongs in a function body must instead be a
named constant defined in constants.py.

Rules
-----
- Strings:  only ``""`` (empty string) is allowed inline.
- Integers:  0, 1, and 2 are allowed (comparisons, indices, binary-search divisor).
- Floats:    none allowed — all floats must be named constants.

Exceptions (not flagged)
------------------------
- Module-level code (constants are defined there by design).
- Docstrings (first statement of a function/class if it is a plain string).
- Dict-key subscripts: the string in ``config["page"]`` is structural, not magic.
- First argument of ``.get()`` calls: same reasoning as dict-key subscripts.
"""

from __future__ import annotations

import ast
from pathlib import Path

# Source modules to audit. constants.py is exempt — it is the definitions file.
_PROJECT_ROOT = Path(__file__).parent.parent
SOURCE_MODULES: tuple[Path, ...] = (
    _PROJECT_ROOT / "style.py",
    _PROJECT_ROOT / "converter.py",
    _PROJECT_ROOT / "convert_to_pdf.py",
)

ALLOWED_STRINGS: frozenset[str] = frozenset({""})
ALLOWED_INTS: frozenset[int] = frozenset({0, 1, 2})
ALLOWED_FLOATS: frozenset[float] = frozenset()


class _MagicLiteralVisitor(ast.NodeVisitor):
    """Collect magic-literal violations from an AST."""

    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.violations: list[str] = []
        self._depth: int = 0  # >0 means we are inside a function body

    # ── Visitors ──────────────────────────────────────────────────────────────

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._depth += 1

        # Check default argument values (e.g. ``font_scale: float = 1.0``).
        all_defaults = node.args.defaults + [
            d for d in node.args.kw_defaults if d is not None
        ]
        for default in all_defaults:
            self.visit(default)

        # Visit the body, skipping the leading docstring if present.
        body = node.body
        has_docstring = (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        )
        for stmt in (body[1:] if has_docstring else body):
            self.visit(stmt)

        self._depth -= 1

    # Async functions follow the same rules.
    visit_AsyncFunctionDef = visit_FunctionDef  # type: ignore[assignment]  # noqa: N815

    def visit_Subscript(self, node: ast.Subscript) -> None:
        """Visit the container but skip plain-string slice (dict-key access)."""
        self.visit(node.value)
        # Allow ``config["page"]`` — the slice is a structural key, not magic.
        slice_is_string_key = isinstance(node.slice, ast.Constant) and isinstance(
            node.slice.value, str
        )
        if not slice_is_string_key:
            self.visit(node.slice)

    def visit_Call(self, node: ast.Call) -> None:
        """Visit call arguments, skipping the key in ``.get("key")`` calls."""
        self.visit(node.func)

        first_arg_is_string = (
            node.args
            and isinstance(node.args[0], ast.Constant)
            and isinstance(node.args[0].value, str)
        )
        is_get_call = isinstance(node.func, ast.Attribute) and node.func.attr == "get"

        # Skip the first arg only when it is the dict-key string in .get("key").
        args_to_check = node.args[1:] if (is_get_call and first_arg_is_string) else node.args
        for arg in args_to_check:
            self.visit(arg)
        for keyword in node.keywords:
            self.visit(keyword.value)

    def visit_Constant(self, node: ast.Constant) -> None:
        if self._depth == 0:
            return  # module-level constants are fine

        value = node.value

        if isinstance(value, bool):
            return  # True/False are not magic

        if isinstance(value, str) and value not in ALLOWED_STRINGS:
            self._flag(node, "string", value)
        elif isinstance(value, float) and value not in ALLOWED_FLOATS:
            self._flag(node, "float", value)
        elif isinstance(value, int) and value not in ALLOWED_INTS:
            self._flag(node, "int", value)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _flag(self, node: ast.Constant, kind: str, value: object) -> None:
        self.violations.append(
            "{}:{}: magic {} {!r} — move to constants.py".format(
                self.filename, node.lineno, kind, value
            )
        )


def _collect_violations(path: Path) -> list[str]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    visitor = _MagicLiteralVisitor(str(path))
    visitor.visit(tree)
    return visitor.violations


# ── Test ──────────────────────────────────────────────────────────────────────


def test_no_magic_literals_in_source_modules() -> None:
    """Fail if any magic string or numeric literal is found in a function body."""
    all_violations: list[str] = []
    for module_path in SOURCE_MODULES:
        all_violations.extend(_collect_violations(module_path))

    if all_violations:
        joined = "\n".join(all_violations)
        raise AssertionError(
            "Magic literals found — move them to constants.py:\n\n" + joined
        )
