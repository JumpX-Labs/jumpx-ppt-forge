#!/usr/bin/env python3
"""Validate slide_plan.json beyond basic JSON shape."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ALLOWED_LAYOUTS = {
    "cover",
    "section-divider",
    "big-idea",
    "two-column",
    "quote",
    "framework",
    "timeline",
    "comparison",
    "image-text",
    "closing",
}


def load_json(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        raise SystemExit(f"missing file: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json: {path}: {exc}")


def project_root_from_plan(plan_path: Path) -> Path:
    if plan_path.parent.name == "source":
        return plan_path.parent.parent
    return plan_path.parent


def validate(plan_path: Path, skill_root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    plan = load_json(plan_path)
    deck_meta = plan.get("deck_meta", {})
    pages = plan.get("pages", [])

    total_pages = deck_meta.get("total_pages")
    if total_pages != len(pages):
        errors.append(f"deck_meta.total_pages={total_pages} but pages has {len(pages)} entries")

    seen: set[str] = set()
    for index, page in enumerate(pages, start=1):
        expected_id = f"P{index:02d}"
        page_id = page.get("page_id")
        if page_id != expected_id:
            errors.append(f"pages[{index - 1}].page_id should be {expected_id}, got {page_id!r}")
        if page_id in seen:
            errors.append(f"duplicate page_id: {page_id}")
        seen.add(page_id)

        layout_type = page.get("layout_type")
        if layout_type not in ALLOWED_LAYOUTS:
            errors.append(f"{page_id}: unsupported layout_type {layout_type!r}")
        else:
            snippet = skill_root / "assets" / "templates" / "layouts" / f"{layout_type}.html.snippet"
            if not snippet.exists():
                errors.append(f"{page_id}: missing layout snippet {snippet}")

        risk = (page.get("image_requirement") or {}).get("text_in_image_risk")
        if risk == "high":
            warnings.append(f"{page_id}: text_in_image_risk is high; prefer HTML or reduce visible text")

    project_root = project_root_from_plan(plan_path)
    style_lock_path = project_root / "source" / "style_lock.json"
    if style_lock_path.exists():
        style_lock = load_json(style_lock_path)
        plan_style = deck_meta.get("style_name")
        lock_style = style_lock.get("style_name")
        if plan_style != lock_style:
            errors.append(f"style mismatch: slide_plan={plan_style!r}, style_lock={lock_style!r}")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slide_plan", type=Path)
    parser.add_argument("--skill-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()

    errors, warnings = validate(args.slide_plan.resolve(), args.skill_root.resolve())
    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)
    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    if errors:
        return 1
    print(f"slide plan ok: {args.slide_plan}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

