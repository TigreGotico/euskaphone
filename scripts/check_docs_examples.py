#!/usr/bin/env python3
"""Run the python blocks of a Markdown page and compare each result with its comment.

A comment run directly under a ``print(...)`` call or a bare expression states
the output: the printed text, or the ``repr`` of the value. A trailing comment
on the same line does the same. Blocks of one page share a namespace. Blocks
fenced ``python`` or ``py`` run; fence code that must not run as ``text``.

A block fenced with no language holds ``input -> output`` lines. Each line
reads its input with ``normalize_text(input, "eu")`` and compares the result
with the output. A comma and a space between inputs list several inputs for one output,
and a trailing ``(source)`` note after two spaces is not part of the output.

A page fails when a block does not parse, when a statement raises, or when a
comment states an output under a statement the script cannot compare (only
``print`` calls, bare expressions and ``for`` loops show output).

    python scripts/check_docs_examples.py README.md docs/quickstart.md
"""

from __future__ import annotations

import ast
import contextlib
import io
import re
import subprocess
import sys
import warnings

warnings.simplefilter("ignore")
BLOCK = re.compile(r"^```(?:python|py)\n(.*?)^```", re.S | re.M)
FENCE = re.compile(r"^```(\w*)\n(.*?)^```", re.S | re.M)
NOTE = re.compile(r"\s{2,}\(.*\)$")


def stated(lines: list[str], stmt: ast.stmt) -> str | None:
    """The output a statement's comments claim, or None when it claims none."""
    tail = lines[stmt.end_lineno - 1]
    if stmt.end_lineno == stmt.lineno and "  # " in tail:
        return tail.split("  # ", 1)[1].strip()
    out = []
    for line in lines[stmt.end_lineno:]:
        text = line.strip()
        if not text.startswith("#"):
            break
        out.append(text[1:].removeprefix(" "))
    return "\n".join(out) if out else None


def check(path: str) -> tuple[int, int]:
    checked = failed = 0
    scope: dict = {"__name__": "__docs__"}
    with open(path, encoding="utf-8") as fh:
        page = fh.read()
    for block in BLOCK.findall(page):
        lines = block.splitlines()
        try:
            body = ast.parse(block).body
        except SyntaxError as err:
            checked += 1
            failed += 1
            print(f"{path}: block does not parse: {err}")
            continue
        for stmt in body:
            source = ast.Module([stmt], [])
            outputs = isinstance(stmt, (ast.Expr, ast.For))
            claim = stated(lines, stmt)
            if claim is not None and not outputs:
                checked += 1
                failed += 1
                print(f"{path}:{stmt.lineno}: comment under a statement that shows no output")
                continue
            buf = io.StringIO()
            shows_value = (
                claim is not None
                and isinstance(stmt, ast.Expr)
                and not (
                    isinstance(stmt.value, ast.Call)
                    and getattr(stmt.value.func, "id", "") == "print"
                )
            )
            try:
                with contextlib.redirect_stdout(buf):
                    if shows_value:
                        expr = ast.Expression(stmt.value)
                        print(repr(eval(compile(expr, path, "eval"), scope)))
                    else:
                        exec(compile(source, path, "exec"), scope)
            except Exception as err:
                if claim is None:
                    checked += 1
                    failed += 1
                    print(f"{path}:{stmt.lineno}: raised {type(err).__name__}: {err}")
                    continue
                buf = io.StringIO(f"{type(err).__name__}: {err}")
            if claim is None:
                continue
            checked += 1
            got = buf.getvalue().rstrip("\n")
            if got != claim:
                failed += 1
                print(f"{path}:{stmt.lineno}: stated {claim!r}, got {got!r}")
    from euskaphone.normalize import normalize_text

    for lang, block in FENCE.findall(page):
        if lang:
            continue
        for line in block.splitlines():
            if " -> " not in line:
                continue
            left, right = (part.strip() for part in line.split("->", 1))
            right = NOTE.sub("", right).strip()
            for source in re.split(r",\s+", left):
                checked += 1
                got = normalize_text(source, "eu")
                if got != right:
                    failed += 1
                    print(f"{path}: {source!r} reads {got!r}, stated {right!r}")
    return checked, failed


def main() -> int:
    """Check each page in its own process, because the lexicon registry is global."""
    paths = sys.argv[1:]
    if len(paths) > 1:
        codes = [subprocess.run([sys.executable, __file__, path]).returncode for path in paths]
        return 1 if any(codes) else 0
    n, bad = check(paths[0])
    print(f"{paths[0]}: {n} outputs checked, {bad} differ")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
