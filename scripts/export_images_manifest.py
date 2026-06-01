#!/usr/bin/env python3
"""Export staged image prompts and images_manifest.json for a slide project."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from datetime import datetime, timezone
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

STOPWORDS = {
    "a",
    "an",
    "and",
    "for",
    "from",
    "in",
    "of",
    "the",
    "to",
    "with",
    "的",
    "是",
    "在",
}


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"missing file: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json: {path}: {exc}")


def read_template(skill_root: Path) -> str:
    return (skill_root / "assets" / "templates" / "image-prompt-template.md").read_text(encoding="utf-8")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def backup(path: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = path.with_name(f"{path.stem}-backup-{stamp}{path.suffix}")
    shutil.copy2(path, backup_path)
    return backup_path


def slugify(text: str, fallback: str) -> str:
    ascii_text = text.lower()
    ascii_text = re.sub(r"[^a-z0-9\s-]", " ", ascii_text)
    words = [word for word in re.split(r"[\s-]+", ascii_text) if word and word not in STOPWORDS]
    slug = "-".join(words)[:30].strip("-")
    return slug or fallback


def unique_filename(index: int, page: dict, used: set[str]) -> str:
    role = page.get("page_role_in_story")
    layout = page.get("layout_type")
    if index == 1 and (role == "cover" or layout == "cover"):
        base = "cover"
    elif role == "back-cover":
        base = "back-cover"
    else:
        base = slugify(page.get("page_title") or page.get("key_message") or "", page.get("layout_type", "slide"))
    candidate = f"{index:02d}-slide-{base}.md"
    if candidate not in used:
        used.add(candidate)
        return candidate
    counter = 2
    while True:
        suffix = f"-{counter}"
        trimmed = base[: max(1, 30 - len(suffix))]
        candidate = f"{index:02d}-slide-{trimmed}{suffix}.md"
        if candidate not in used:
            used.add(candidate)
            return candidate
        counter += 1


def yaml_quote(value: object) -> str:
    return json.dumps("" if value is None else str(value), ensure_ascii=False)


def yaml_list(items: list[str], indent: str = "  ") -> str:
    if not items:
        return f"{indent}[]"
    return "\n".join(f"{indent}- {yaml_quote(item)}" for item in items)


def md_list(items: list[str]) -> str:
    if not items:
        return "- (none)"
    return "\n".join(f"- {item}" for item in items)


def replace(template: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        template = template.replace(f"{{{{{key}}}}}", value)
    return template


def selected_pages(plan: dict, include_all: bool) -> list[tuple[int, dict]]:
    pages = list(enumerate(plan["pages"], start=1))
    if include_all:
        return pages
    output_mode = plan.get("deck_meta", {}).get("output_mode", "html-only")
    if output_mode == "image-first":
        return pages
    if output_mode in {"mixed", "html-takeover", "html-only-with-prompts"}:
        return [(index, page) for index, page in pages if (page.get("image_requirement") or {}).get("needed") is True]
    return []


def backend_from_env(explicit: str | None) -> str:
    backend = explicit or os.environ.get("IMAGE_BACKEND") or "none"
    backend = backend.strip().lower()
    if backend not in BACKENDS:
        raise SystemExit(f"unsupported backend: {backend}")
    return backend


def visual_composition(page: dict, style_lock: dict) -> str:
    image_req = page.get("image_requirement") or {}
    parts = [
        f"Create a {page.get('layout_type')} slide image for this purpose: {page.get('page_goal')}.",
        f"Main message: {page.get('key_message')}.",
        f"Visual direction: {page.get('visual_direction')}.",
        f"Image intent: {image_req.get('intent', 'none')}.",
        f"Use the deck style: {style_lock.get('image_style')}.",
    ]
    return " ".join(part for part in parts if part)


def prompt_values(index: int, page: dict, plan: dict, style_lock: dict, filename: str, backend: str) -> dict[str, str]:
    text = page.get("on_slide_text") or {}
    body = text.get("body") or []
    image_req = page.get("image_requirement") or {}
    aspect = image_req.get("aspect_ratio_override") or plan.get("deck_meta", {}).get("canvas_ratio") or style_lock.get("canvas_ratio") or "16:9"
    target = image_req.get("generated_image_path") or f"images/slide-{index:02d}.png"
    negative = list(style_lock.get("forbidden") or [])
    negative.extend(style_lock.get("negative_constraints") or [])
    negative.extend([
        "no watermarks",
        "no logos unless explicitly requested",
        "no tiny unreadable text",
        "no distorted typography",
    ])
    composition = visual_composition(page, style_lock)
    return {
        "slide_id": page.get("page_id", f"P{index:02d}"),
        "slide_title": page.get("page_title", ""),
        "slide_title_yaml": yaml_quote(page.get("page_title")),
        "filename": filename,
        "visible_headline": text.get("headline") or page.get("page_title") or "",
        "visible_headline_yaml": yaml_quote(text.get("headline") or page.get("page_title")),
        "visible_sub_headline": text.get("sub_headline") or "",
        "visible_sub_headline_yaml": yaml_quote(text.get("sub_headline")),
        "visible_body_yaml": yaml_list(body, indent="    "),
        "visual_composition": yaml_quote(composition),
        "style_preset": style_lock.get("style_name", plan.get("deck_meta", {}).get("style_name", "teaching-clean")),
        "negative_constraints_yaml": yaml_list(negative),
        "target_aspect_ratio": aspect,
        "image_backend": backend,
        "backend_model": "",
        "reference_image": "",
        "session_id": "",
        "generated_image_path": target,
        "slide_purpose": page.get("page_goal", ""),
        "visible_body_markdown": md_list(body),
        "composition_body": composition,
        "visual_hierarchy": f"Lead with the headline, support with the key message, and keep body text minimal for {style_lock.get('density', 'medium')} density.",
        "image_style": style_lock.get("image_style", ""),
        "density": style_lock.get("density", ""),
        "primary_color": style_lock.get("primary_color", ""),
        "accent_color": style_lock.get("accent_color", ""),
        "background_color": style_lock.get("background_color", ""),
        "negative_constraints_markdown": md_list(negative),
    }


def write_prompt(path: Path, content: str, force: bool) -> str:
    if path.exists() and not force:
        return "kept"
    if path.exists() and force:
        backup(path)
    path.write_text(content, encoding="utf-8")
    return "written"


def write_summary(project_dir: Path, entries: list[dict], plan: dict) -> None:
    lines = [
        "# Image Prompts",
        "",
        f"**Deck**: {plan.get('deck_meta', {}).get('deck_title', '')}",
        f"**Generated**: {now_iso()}",
        "",
        "| Slide | Prompt | Target Image | Status |",
        "|-------|--------|--------------|--------|",
    ]
    for entry in entries:
        lines.append(
            f"| {entry['slide_id']} | `{entry['prompt_file']}` | `{entry.get('image_file', '')}` | `{entry['status']}` |"
        )
    if not entries:
        lines.extend(["", "No image prompts were selected for this output mode."])
    (project_dir / "source" / "image_prompts.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def export(project_dir: Path, skill_root: Path, include_all: bool, force: bool, backend: str) -> dict:
    source_dir = project_dir / "source"
    plan = load_json(source_dir / "slide_plan.json")
    style_lock_path = source_dir / "style_lock.json"
    style_lock = load_json(style_lock_path)
    template = read_template(skill_root)

    prompts_dir = project_dir / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)

    used: set[str] = set()
    entries: list[dict] = []
    changed = {"written": 0, "kept": 0}
    for index, page in selected_pages(plan, include_all):
        # Re-read before each page to honor Context Lock.
        page_lock = load_json(style_lock_path)
        filename = unique_filename(index, page, used)
        prompt_path = prompts_dir / filename
        values = prompt_values(index, page, plan, page_lock, filename, backend)
        content = replace(template, values)
        outcome = write_prompt(prompt_path, content, force=force)
        changed[outcome] = changed.get(outcome, 0) + 1
        entries.append(
            {
                "slide_id": page.get("page_id", f"P{index:02d}"),
                "prompt_file": f"prompts/{filename}",
                "image_file": "",
                "backend": backend,
                "aspect_ratio": values["target_aspect_ratio"],
                "status": "pending",
                "attempts": 0,
            }
        )

    manifest = {
        "deck_title": plan.get("deck_meta", {}).get("deck_title", style_lock.get("deck_title", "")),
        "created_at": now_iso(),
        "default_backend": backend,
        "default_aspect_ratio": plan.get("deck_meta", {}).get("canvas_ratio") or style_lock.get("canvas_ratio", "16:9"),
        "entries": entries,
    }
    manifest_path = project_dir / "images_manifest.json"
    if manifest_path.exists() and force:
        backup(manifest_path)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_summary(project_dir, entries, plan)
    manifest["_changed"] = changed
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", type=Path)
    parser.add_argument("--skill-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--include-all", action="store_true", help="stage prompts for all pages regardless of output mode")
    parser.add_argument("--force", action="store_true", help="backup and overwrite existing prompt files")
    parser.add_argument("--backend", choices=sorted(BACKENDS), default=None, help="backend id to write into prompts/manifest")
    args = parser.parse_args()

    backend = backend_from_env(args.backend)
    manifest = export(args.project_dir.resolve(), args.skill_root.resolve(), args.include_all, args.force, backend)
    changed = manifest.pop("_changed")
    print(
        f"exported {len(manifest['entries'])} prompt entries "
        f"(written={changed.get('written', 0)}, kept={changed.get('kept', 0)}) "
        f"to {args.project_dir / 'images_manifest.json'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
