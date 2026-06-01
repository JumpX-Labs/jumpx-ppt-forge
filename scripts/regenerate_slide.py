#!/usr/bin/env python3
"""Mark selected slides for regeneration and refresh derived outputs."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"missing file: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json: {path}: {exc}")


def save_json(path: Path, data: dict) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def parse_selectors(values: list[str]) -> set[str]:
    selectors: set[str] = set()
    for value in values:
        for token in value.split(","):
            token = token.strip()
            if token:
                selectors.add(token)
    if not selectors:
        raise SystemExit("at least one slide selector is required")
    return selectors


def selector_candidates(entry: dict, entry_number: int) -> set[str]:
    slide_id = str(entry.get("slide_id", ""))
    prompt_name = Path(str(entry.get("prompt_file", ""))).name
    candidates = {
        str(entry_number),
        f"{entry_number:02d}",
        slide_id,
        slide_id.lower(),
        prompt_name,
    }
    if slide_id.upper().startswith("P") and slide_id[1:].isdigit():
        candidates.add(str(int(slide_id[1:])))
    return candidates


def selected_entries(manifest: dict, selectors: set[str]) -> list[tuple[int, dict]]:
    selected: list[tuple[int, dict]] = []
    lowered = {selector.lower() for selector in selectors}
    for entry_number, entry in enumerate(manifest.get("entries", []), start=1):
        candidates = selector_candidates(entry, entry_number)
        if selectors & candidates or lowered & {candidate.lower() for candidate in candidates}:
            selected.append((entry_number, entry))
    if not selected:
        raise SystemExit(f"no manifest entries matched: {', '.join(sorted(selectors))}")
    return selected


def project_relative_path(project_dir: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        raise SystemExit(f"path must be project-relative: {raw_path}")
    resolved = (project_dir / path).resolve()
    root = project_dir.resolve()
    if root != resolved and root not in resolved.parents:
        raise SystemExit(f"path escapes project directory: {raw_path}")
    return resolved


def backup_file(project_dir: Path, backup_root: Path, raw_path: str, *, move: bool) -> str | None:
    if not raw_path:
        return None
    source = project_relative_path(project_dir, raw_path)
    if not source.exists():
        return None
    target = backup_root / source.relative_to(project_dir)
    target.parent.mkdir(parents=True, exist_ok=True)
    if move:
        shutil.move(str(source), str(target))
    else:
        shutil.copy2(source, target)
    return str(target.relative_to(project_dir))


def append_log(project_dir: Path, lines: list[str]) -> None:
    source_dir = project_dir / "source"
    source_dir.mkdir(parents=True, exist_ok=True)
    log_path = source_dir / "regeneration_log.md"
    existing = log_path.read_text(encoding="utf-8") if log_path.exists() else "# Regeneration Log\n\n"
    log_path.write_text(existing.rstrip() + "\n\n" + "\n".join(lines) + "\n", encoding="utf-8")


def run_command(command: list[str], cwd: Path) -> None:
    print("+ " + " ".join(command))
    subprocess.run(command, cwd=cwd, check=True)


def mark_for_regeneration(project_dir: Path, selectors: set[str], args: argparse.Namespace) -> list[str]:
    manifest_path = project_dir / "images_manifest.json"
    manifest = load_json(manifest_path)
    selected = selected_entries(manifest, selectors)
    backup_root = project_dir / "backups" / f"regenerate-{now_stamp()}"
    changed_ids: list[str] = []
    log_lines = [f"## {now_iso()}", ""]

    for entry_number, entry in selected:
        slide_id = str(entry.get("slide_id", f"P{entry_number:02d}"))
        prompt_file = str(entry.get("prompt_file", ""))
        image_file = str(entry.get("image_file") or f"images/slide-{entry_number:02d}.png")
        prompt_backup = backup_file(project_dir, backup_root, prompt_file, move=False)
        image_backup = None
        if args.mode != "prompts-only":
            image_backup = backup_file(project_dir, backup_root, image_file, move=not args.keep_old_image)

        entry["status"] = "regenerate-requested"
        entry["updated_at"] = now_iso()
        entry["regeneration_requested_at"] = entry["updated_at"]
        entry["regeneration_mode"] = args.mode
        entry["image_file"] = "" if args.mode != "prompts-only" else entry.get("image_file", "")
        entry.pop("error_message", None)
        changed_ids.append(slide_id)

        log_lines.append(f"- `{slide_id}` marked `regenerate-requested` ({args.mode})")
        if prompt_backup:
            log_lines.append(f"  - prompt backup: `{prompt_backup}`")
        if image_backup:
            log_lines.append(f"  - image backup: `{image_backup}`")

    manifest["updated_at"] = now_iso()
    save_json(manifest_path, manifest)
    append_log(project_dir, log_lines)
    print(f"marked {len(changed_ids)} slide(s): {', '.join(changed_ids)}")
    return changed_ids


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", type=Path)
    parser.add_argument("slides", nargs="+", help="slide ids or indexes, comma-separated values accepted")
    parser.add_argument("--skill-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--mode", choices=["images-only", "prompts-only", "full"], default="images-only")
    parser.add_argument("--keep-old-image", action="store_true", help="copy old image to backup but keep it in place")
    parser.add_argument("--generate", action="store_true", help="run generate_images.py after marking")
    parser.add_argument("--backend", help="backend override forwarded to generate_images.py")
    parser.add_argument("--no-build-html", action="store_true", help="skip build_html.py after marking/generation")
    args = parser.parse_args()

    project_dir = args.project_dir.resolve()
    skill_root = args.skill_root.resolve()
    selectors = parse_selectors(args.slides)
    slide_ids = mark_for_regeneration(project_dir, selectors, args)

    if args.generate:
        command = [
            sys.executable,
            str(skill_root / "scripts" / "generate_images.py"),
            str(project_dir),
            "--only",
            ",".join(slide_ids),
            "--force",
        ]
        if args.backend:
            command.extend(["--backend", args.backend])
        run_command(command, cwd=skill_root)

    if not args.no_build_html:
        run_command(
            [sys.executable, str(skill_root / "scripts" / "build_html.py"), str(project_dir)],
            cwd=skill_root,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
