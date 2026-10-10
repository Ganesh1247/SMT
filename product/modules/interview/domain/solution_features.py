"""Derive interview prompts from the learner's own L3 solution. Pure functions.

Learner code is untrusted text: only sanitised identifiers and fixed vocabulary reach prompts."""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field

CRITERIA = ("explain", "justify_approach", "complexity", "edge_cases", "adapt")
_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,39}$")
_SQL_HINT = re.compile(r"^\s*(with|select)\b", re.IGNORECASE)


@dataclass(frozen=True)
class Features:
    functions: list[str] = field(default_factory=list)
    loops: int = 0
    structures: frozenset = frozenset()
    is_sql: bool = False


@dataclass(frozen=True)
class Prompt:
    criterion: str
    text: str
    keywords: tuple
    follow_up: str


def analyse(code: str) -> Features:
    code = code or ""
    if _SQL_HINT.match(code):
        low = code.lower()
        structs = {n for n, pat in (("join", r"\bjoin\b"), ("grouping", r"\bgroup\s+by\b"),
                                    ("filter", r"\bwhere\b"), ("window", r"\bover\s*\("),
                                    ("subquery", r"\(\s*select\b")) if re.search(pat, low)}
        return Features(is_sql=True, structures=frozenset(structs))
    try:
        tree = ast.parse(code)
    except (SyntaxError, ValueError, RecursionError):
        return Features()
    funcs, loops, structs = [], 0, set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and _IDENT.match(node.name) and len(funcs) < 3:
            funcs.append(node.name)
        elif isinstance(node, (ast.For, ast.While, ast.comprehension)):
            loops += 1
        elif isinstance(node, (ast.Dict, ast.DictComp)):
            structs.add("dictionary")
        elif isinstance(node, (ast.Set, ast.SetComp)):
            structs.add("set")
        elif isinstance(node, ast.Call):
            name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
            if name in ("sorted", "sort"):
                structs.add("sorting")
            elif name in ("dict", "defaultdict", "Counter"):
                structs.add("dictionary")
            elif name == "set":
                structs.add("set")
    return Features(functions=funcs, loops=loops, structures=frozenset(structs))


def mutation_constraint(f: Features) -> str:
    if f.is_sql:
        return "the table is now far too large to scan, so the query must filter on an indexed column first."
    if "dictionary" in f.structures or "set" in f.structures:
        return "memory is limited, so you may only use a constant amount of extra space."
    if f.loops >= 2:
        return "the data must be processed in a single pass."
    if "sorting" in f.structures:
        return "the input is already sorted and too large to copy."
    return "the input arrives as a stream and cannot be held in memory."


def build_prompts(f: Features) -> list[Prompt]:
    fn = f.functions[0] if f.functions else "your solution"
    ref = f"`{fn}`" if f.functions else fn
    structure = ", ".join(sorted(f.structures)) or ("loops" if f.loops else "the approach you used")
    return [
        Prompt("explain", f"Walk me through how {ref} works, step by step, in your own words.",
               ("loop", "iterate", "return", "function", "dictionary", "list", "set", "sort", "first", "then", "select", "join"),
               "Could you take one concrete input and trace what happens, step by step?"),
        Prompt("justify_approach", f"Why did you choose {structure} here? What alternative did you consider?",
               ("because", "instead", "alternative", "faster", "simpler", "readable", "trade", "since", "rather"),
               "What would have been the main downside of the alternative approach?"),
        Prompt("complexity", f"What are the time and space complexity of {ref}, and which part dominates?",
               ("o(n", "o(1", "o(log", "linear", "quadratic", "constant", "time", "space", "memory"),
               "Please state the time and the space cost separately, in terms of the input size."),
        Prompt("edge_cases", "Which edge cases does your solution handle, and which might it get wrong?",
               ("empty", "none", "null", "zero", "negative", "duplicate", "single", "large", "invalid", "missing"),
               "What happens with empty input, or with duplicate values?"),
        Prompt("adapt", f"New requirement: {mutation_constraint(f)} How would you change {ref}?",
               ("instead", "change", "modify", "would", "replace", "stream", "one pass", "generator", "index", "constant"),
               "Which specific lines or steps would you change first?"),
    ]


def needs_follow_up(answer: str, prompt: Prompt) -> bool:
    """Rule: fewer than 12 words, or no keyword from the expected vocabulary."""
    words = answer.split()
    low = answer.lower()
    return len(words) < 12 or not any(k in low for k in prompt.keywords)
