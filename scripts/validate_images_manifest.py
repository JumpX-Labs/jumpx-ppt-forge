#!/usr/bin/env python3
"""Validate images_manifest.json and staged prompt frontmatter."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


BACKENDS = {
    "none",
    "native",
    "openai",
    "gemini",
    "nanobanana",
    "qwen",
    "zhipu",
    "volcengine",
    "minimax",
    "stability",
    "bfl",
    "ideogram",
    "siliconflow",
    "fal",
    "replicate",
    "openrouter",
    "modelscope",
}

STATUSES = {"pending", "generating", "ok", "failed", "needs-manual", "regenerate-requested"}

REQUIRED_PROMPT_FIELDS = [
    "slide_id",
    "slide_title",
    "visible_text",
    "visual_composition",
    "style_preset",
    "style_lock_ref",
    "negative_constraints",
    "target_aspect_ratio",
    "image_backend",
    "generated_image_path",
]


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"missing file: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json: {path}: {exc}")


def frontmatter(text: str) -> str:
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.S)
    return match.group(1) if match else ""


def validate_prompt(path: Path, slide_id: str) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"missing prompt file: {path}"]
    fm = frontmatter(path.read_text(encoding="utf-8"))
    if not fm:
        return [f"missing frontmatter: {path}"]
    for field in REQUIRED_PROMPT_FIELDS:
        if not re.search(rf"^{re.escape(field)}:", fm, flags=re.M):
            errors.append(f"{path}: missing frontmatter field {field}")
    if f'slide_id: "{slide_id}"' not in fm and f"slide_id: {slide_id}" not in fm:
        errors.append(f"{path}: slide_id does not match manifest entry {slide_id}")
    return errors


def validate(project_dir: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    manifest_path = project_dir / "images_manifest.json"
    manifest = load_json(manifest_path)

    for field in ("deck_title", "created_at", "default_backend", "entries"):
        if field not in manifest:
            errors.append(f"manifest missing {field}")
    if manifest.get("default_backend") not in BACKENDS:
        errors.append(f"unsupported default_backend: {manifest.get('default_backend')!r}")
    entries = manifest.get("entries", [])
    if not isinstance(entries, list):
        errors.append("manifest entries must be an array")
        return errors, warnings

    seen: set[str] = set()
    for entry in entries:
        slide_id = entry.get("slide_id")
        if not slide_id:
            errors.append("manifest entry missing slide_id")
            continue
        if slide_id in seen:
            errors.append(f"duplicate manifest slide_id: {slide_id}")
        seen.add(slide_id)
        if entry.get("status") not in STATUSES:
            errors.append(f"{slide_id}: unsupported status {entry.get('status')!r}")
        backend = entry.get("backend", manifest.get("default_backend"))
        if backend not in BACKENDS:
            errors.append(f"{slide_id}: unsupported backend {backend!r}")
        prompt_file = entry.get("prompt_file", "")
        if not prompt_file:
            errors.append(f"{slide_id}: missing prompt_file")
        else:
            errors.extend(validate_prompt(project_dir / prompt_file, slide_id))
        status = entry.get("status")
        image_file = entry.get("image_file", "")
        if status == "ok" and not image_file:
            errors.append(f"{slide_id}: status ok requires image_file")
        if status == "pending" and image_file:
            warnings.append(f"{slide_id}: pending entry has image_file set")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", type=Path)
    args = parser.parse_args()

    errors, warnings = validate(args.project_dir.resolve())
    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)
    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    if errors:
        return 1
    print(f"images manifest ok: {args.project_dir / 'images_manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

