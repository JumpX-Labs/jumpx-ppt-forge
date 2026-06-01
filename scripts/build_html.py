#!/usr/bin/env python3
"""Build a self-contained HTML slide deck from source/slide_plan.json."""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path


PLACEHOLDER_RE = re.compile(r"{{\s*([a-zA-Z0-9_]+)\s*}}")


def load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise SystemExit(f"missing file: {path}")


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"missing file: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json: {path}: {exc}")


def esc(value: object) -> str:
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def replace_vars(text: str, values: dict[str, str]) -> str:
    def repl(match: re.Match[str]) -> str:
        return values.get(match.group(1), "")

    return PLACEHOLDER_RE.sub(repl, text)


def css_vars(style_lock: dict) -> str:
    mapping = {
        "--asp-bg": style_lock.get("background_color"),
        "--asp-ink": style_lock.get("primary_color"),
        "--asp-accent": style_lock.get("accent_color"),
        "--asp-font-heading": style_lock.get("font_heading"),
        "--asp-font-body": style_lock.get("font_body"),
        "--asp-muted": style_lock.get("text_secondary_color", "#64748B"),
        "--asp-line": style_lock.get("border_color", "#D7DEE8"),
    }
    lines = [":root {"]
    for key, value in mapping.items():
        if value:
            lines.append(f"  {key}: {value};")
    lines.append("}")
    return "\n".join(lines)


def list_items(items: list[str]) -> str:
    if not items:
        return ""
    rendered = "\n".join(f"        <li>{esc(item)}</li>" for item in items)
    return f'<ul class="body-list">\n{rendered}\n      </ul>'


def tiles(items: list[str]) -> str:
    if not items:
        return ""
    result: list[str] = []
    for item in items[:6]:
        if ":" in item:
            title, body = item.split(":", 1)
        elif "：" in item:
            title, body = item.split("：", 1)
        else:
            title, body = item, ""
        result.append(
            '    <article class="tile">'
            f"<h3>{esc(title.strip())}</h3>"
            f"<p>{esc(body.strip())}</p>"
            "</article>"
        )
    return "\n".join(result)


def steps(items: list[str]) -> str:
    result: list[str] = []
    for index, item in enumerate(items[:6], start=1):
        if ":" in item:
            title, body = item.split(":", 1)
        elif "：" in item:
            title, body = item.split("：", 1)
        else:
            title, body = f"Step {index}", item
        result.append(
            '      <li class="step">'
            f'<span class="step-num">{index}</span>'
            "<div>"
            f'<h3 class="step-title">{esc(title.strip())}</h3>'
            f'<p class="step-copy">{esc(body.strip())}</p>'
            "</div>"
            "</li>"
        )
    return "\n".join(result)


def comparison_panels(items: list[str]) -> str:
    first = items[:4] if items else ["Before: unclear and hard to reuse", "After: visible, reusable slide assets"]
    result: list[str] = []
    for item in first:
        if ":" in item:
            title, body = item.split(":", 1)
        elif "：" in item:
            title, body = item.split("：", 1)
        else:
            title, body = item, ""
        result.append(
            '    <article class="panel">'
            f"<h3>{esc(title.strip())}</h3>"
            f"<p>{esc(body.strip())}</p>"
            "</article>"
        )
    return "\n".join(result)


def image_candidate(project_dir: Path, page_number: int, image_src: str) -> str:
    candidates = [image_src] if image_src else []
    candidates.extend(f"images/slide-{page_number:02d}.{ext}" for ext in ("png", "jpg", "jpeg", "webp"))
    for candidate in candidates:
        if not candidate:
            continue
        allowed = re.match(r"^images/slide-[0-9]{2,3}\.(png|jpg|jpeg|webp)$", candidate)
        if allowed and (project_dir / candidate).exists():
            return candidate
    return ""


def image_block(project_dir: Path, page_number: int, image_src: str, label: str, needed: bool) -> str:
    candidate = image_candidate(project_dir, page_number, image_src)
    allowed = re.match(r"^images/slide-[0-9]{2,3}\.(png|jpg|jpeg|webp)$", candidate)
    if allowed:
        return f'<img src="{esc(candidate)}" alt="{esc(label)}">'
    if needed:
        pending = f"Image pending (slide-{page_number:02d})"
        if label:
            pending = f"{pending}: {label}"
        return f'<span class="image-pending">{esc(pending)}</span>'
    return f"<span>{esc(label or 'No image required')}</span>"


def two_column_values(page: dict, body: list[str]) -> tuple[str, list[str]]:
    if page.get("layout_type") == "two-column" and len(body) >= 2:
        return body[0], body[1:]
    return page.get("key_message", ""), body


def page_values(page: dict, deck_meta: dict, style_lock: dict, index: int, total: int, project_dir: Path) -> dict[str, str]:
    text = page.get("on_slide_text") or {}
    body = text.get("body") or []
    image_req = page.get("image_requirement") or {}
    generated = image_req.get("generated_image_path", "")
    two_column_lead, body_items = two_column_values(page, body)
    return {
        "deck_title": esc(deck_meta.get("deck_title") or style_lock.get("deck_title")),
        "page_title": esc(page.get("page_title")),
        "page_role": esc(page.get("page_role_in_story")),
        "key_message": esc(page.get("key_message")),
        "two_column_lead": esc(two_column_lead),
        "headline": esc(text.get("headline") or page.get("page_title")),
        "sub_headline": esc(text.get("sub_headline")),
        "caption": esc(text.get("caption")),
        "speaker_notes": esc(page.get("speaker_notes")),
        "body_items": list_items(body_items),
        "tiles": tiles(body),
        "steps": steps(body),
        "comparison_panels": comparison_panels(body),
        "image_block": image_block(project_dir, index, generated, page.get("visual_direction", ""), bool(image_req.get("needed"))),
        "page_number": str(index),
        "total_pages": str(total),
    }


def render_slide(page: dict, deck_meta: dict, style_lock: dict, index: int, total: int, skill_root: Path, project_dir: Path) -> str:
    # Intentional per-page read to honor the Context Lock rule.
    style_lock_path = None
    snippet_path = skill_root / "assets" / "templates" / "layouts" / f"{page['layout_type']}.html.snippet"
    snippet = load_text(snippet_path)
    values = page_values(page, deck_meta, style_lock, index, total, project_dir)
    body = replace_vars(snippet, values)
    attrs = {
        "class": "slide",
        "data-page-id": page["page_id"],
        "data-layout": page["layout_type"],
        "data-role": page["page_role_in_story"],
    }
    attr_text = " ".join(f'{key}="{esc(value)}"' for key, value in attrs.items())
    return f"  <section {attr_text}>\n{body}\n  </section>"


def index_items(pages: list[dict]) -> str:
    result: list[str] = []
    for index, page in enumerate(pages):
        result.append(
            f'      <button class="index-card" type="button" role="listitem" data-index-target="{index}">'
            f"<strong>{index + 1:02d}</strong><span>{esc(page.get('page_title'))}</span></button>"
        )
    return "\n".join(result)


def build(project_dir: Path, skill_root: Path, minimal: bool = False) -> Path:
    source_dir = project_dir / "source"
    plan = load_json(source_dir / "slide_plan.json")
    style_lock = load_json(source_dir / "style_lock.json")
    deck_meta = plan["deck_meta"]
    pages = plan["pages"]
    style_name = style_lock["style_name"]

    template_name = "web-slide-template-minimal.html" if minimal else "web-slide-template.html"
    template = load_text(skill_root / "assets" / "templates" / template_name)
    base_css = load_text(skill_root / "assets" / "styles" / f"{style_name}.css")
    style_css = css_vars(style_lock) + "\n\n" + base_css

    slides = []
    for index, page in enumerate(pages, start=1):
        # Re-read lock before each page; build uses the current file as source of truth.
        page_lock = load_json(source_dir / "style_lock.json")
        slides.append(render_slide(page, deck_meta, page_lock, index, len(pages), skill_root, project_dir))

    html_out = replace_vars(
        template,
        {
            "lang": esc(deck_meta.get("language", "zh-CN")),
            "deck_title": esc(deck_meta.get("deck_title", style_lock.get("deck_title", "Slides"))),
            "style_css": style_css,
            "slides": "\n".join(slides),
            "index_items": index_items(pages),
            "total_pages": str(len(pages)),
        },
    )
    output = project_dir / "index.html"
    output.write_text(html_out, encoding="utf-8")
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", type=Path)
    parser.add_argument("--skill-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--minimal", action="store_true")
    args = parser.parse_args()

    output = build(args.project_dir.resolve(), args.skill_root.resolve(), minimal=args.minimal)
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
