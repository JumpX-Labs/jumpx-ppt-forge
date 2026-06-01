#!/usr/bin/env python3
"""Validate style_lock.json for Phase 1 rendering."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED = {
    "deck_title",
    "audience",
    "canvas_ratio",
    "style_name",
    "primary_color",
    "accent_color",
    "background_color",
    "font_heading",
    "font_body",
    "image_style",
    "density",
    "forbidden",
}

HEX_RE = re.compile(r"^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})$")


def load_json(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        raise SystemExit(f"missing file: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json: {path}: {exc}")


def validate(lock_path: Path, skill_root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    lock = load_json(lock_path)

    missing = sorted(REQUIRED - set(lock))
    if missing:
        errors.append("missing required fields: " + ", ".join(missing))

    for key in ("primary_color", "accent_color", "background_color"):
        value = lock.get(key)
        if not isinstance(value, str) or not HEX_RE.match(value):
            errors.append(f"{key} must be a CSS hex color, got {value!r}")

    style_name = lock.get("style_name")
    preset = skill_root / "assets" / "style-presets" / f"{style_name}.json"
    css = skill_root / "assets" / "styles" / f"{style_name}.css"
    if not preset.exists():
        errors.append(f"missing style preset: {preset}")
    if not css.exists():
        errors.append(f"missing style css: {css}")

    if lock.get("canvas_ratio") != "16:9":
        warnings.append("Phase 1 HTML template is optimized for 16:9")

    forbidden = lock.get("forbidden")
    if not isinstance(forbidden, list):
        errors.append("forbidden must be an array")

    for key in ("font_heading", "font_body"):
        value = lock.get(key, "")
        if any(token in str(value) for token in (";", "{", "}")):
            errors.append(f"{key} contains unsafe CSS token")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("style_lock", type=Path)
    parser.add_argument("--skill-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()

    errors, warnings = validate(args.style_lock.resolve(), args.skill_root.resolve())
    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)
    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    if errors:
        return 1
    print(f"style lock ok: {args.style_lock}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
