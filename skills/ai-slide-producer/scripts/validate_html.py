#!/usr/bin/env python3
"""Validate generated AI Slide Producer HTML."""

from __future__ import annotations

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


PLACEHOLDER_RE = re.compile(r"{{\s*[a-zA-Z0-9_]+\s*}}")


class SlideParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.sections: list[dict[str, str]] = []
        self.has_deck = False
        self.has_controls = False
        self.has_index = False
        self.scripts = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {key: value or "" for key, value in attrs}
        if tag == "main" and data.get("id") == "deck":
            self.has_deck = True
        if tag == "section" and "slide" in data.get("class", "").split():
            self.sections.append(data)
        if tag == "nav" and "slide-controls" in data.get("class", "").split():
            self.has_controls = True
        if tag == "div" and data.get("id") == "index":
            self.has_index = True
        if tag == "script":
            self.scripts += 1


def validate(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return [f"missing html: {path}"], warnings

    if PLACEHOLDER_RE.search(text):
        errors.append("residual {{placeholder}} found")
    if "<script>alert" in text.lower():
        warnings.append("possible unescaped script-looking text found")

    parser = SlideParser()
    parser.feed(text)
    if not parser.has_deck:
        errors.append("missing main#deck")
    if not parser.sections:
        errors.append("no .slide sections found")
    if not parser.has_controls:
        errors.append("missing .slide-controls")
    if not parser.has_index:
        errors.append("missing ESC index container")
    if parser.scripts == 0:
        errors.append("missing inline slide script")

    page_ids = [section.get("data-page-id", "") for section in parser.sections]
    if len(page_ids) != len(set(page_ids)):
        errors.append("duplicate data-page-id in HTML")
    for index, page_id in enumerate(page_ids, start=1):
        expected = f"P{index:02d}"
        if page_id != expected:
            errors.append(f"section {index} data-page-id should be {expected}, got {page_id!r}")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path)
    args = parser.parse_args()

    errors, warnings = validate(args.html.resolve())
    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)
    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    if errors:
        return 1
    print(f"html ok: {args.html}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

