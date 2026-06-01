#!/usr/bin/env python3
"""Generate raster images from staged prompts and images_manifest.json.

Uses synchronous OpenAI-compatible POST {OPENAI_BASE_URL}/images/generations.
Some gateways also expose async jobs (POST .../images/jobs/generations,
GET .../images/jobs/{job_id}); those are documented in references/09-image-renderer.md
but not implemented here yet.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


SUPPORTED_BACKENDS = {"openai", "gemini", "nanobanana"}
PASSIVE_BACKENDS = {
    "none",
    "native",
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
PROCESSABLE_STATUSES = {"pending", "failed", "needs-manual", "regenerate-requested"}
OPENAI_SIZES_16_9 = {
    "512px": "1280x720",
    "1K": "1280x720",
    "2K": "2048x1152",
    "4K": "3840x2160",
}
OPENAI_SIZE_BY_ASPECT = {
    "1:1": "1024x1024",
    "16:9": "1280x720",
    "9:16": "720x1280",
    "3:2": "1248x832",
    "2:3": "832x1248",
    "4:3": "1024x768",
    "3:4": "768x1024",
    "4:5": "896x1120",
    "5:4": "1120x896",
    "21:9": "1280x544",
}
IMAGE_QUALITY = {
    "512px": "low",
    "1K": "medium",
    "2K": "high",
    "4K": "high",
}
ENV_PREFIXES = (
    "IMAGE_",
    "OPENAI_",
    "GEMINI_",
    "NANOBANANA_",
)

# Google Gemini Image API (product name: Nano Banana). See references/09-image-renderer.md.
NANOBANANA_DEFAULT_MODEL = "gemini-3.1-flash-image-preview"  # Nano Banana 2
NANOBANANA_MODEL_ALIASES = {
    "nano-banana-2": "gemini-3.1-flash-image-preview",
    "nano-banana-pro": "gemini-3-pro-image-preview",
    "nano-banana": "gemini-2.5-flash-image",
}


class GenerationSkip(Exception):
    """A non-fatal skip that should leave the manifest entry pending."""


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


def strip_env_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def strip_inline_comment(value: str) -> str:
    stripped = value.lstrip()
    if stripped.startswith(("'", '"')):
        quote = stripped[0]
        end = stripped.find(quote, 1)
        if end != -1:
            head_len = len(value) - len(stripped) + end + 1
            tail = value[head_len:]
            hash_pos = tail.find("#")
            return value if hash_pos == -1 else value[: head_len + hash_pos]
    hash_pos = value.find("#")
    return value if hash_pos == -1 else value[:hash_pos]


def load_env(project_dir: Path, skill_root: Path) -> Path | None:
    candidates = [
        Path.cwd() / ".env",
        project_dir / ".env",
        skill_root / ".env",
        Path.home() / ".ai-slide-producer" / ".env",
    ]
    env_path = next((path for path in candidates if path.exists()), None)
    if env_path is None:
        return None
    for lineno, raw_line in enumerate(env_path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        if "=" not in line:
            raise SystemExit(f"invalid env line {env_path}:{lineno}: expected KEY=VALUE")
        key, value = line.split("=", 1)
        key = key.strip()
        if not any(key.startswith(prefix) for prefix in ENV_PREFIXES):
            continue
        os.environ.setdefault(key, strip_env_quotes(strip_inline_comment(value).strip()))
    return env_path


def prompt_parts(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, flags=re.S)
    if not match:
        return {}, text.strip()
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line or line.startswith(" "):
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                value = value[1:-1]
        fields[key.strip()] = str(value)
    return fields, match.group(2).strip()


def safe_project_path(project_dir: Path, raw_path: str, *, default: str) -> Path:
    candidate = Path(raw_path or default)
    if candidate.is_absolute():
        raise ValueError(f"image path must be project-relative: {raw_path}")
    normalized = (project_dir / candidate).resolve()
    root = project_dir.resolve()
    if root != normalized and root not in normalized.parents:
        raise ValueError(f"image path escapes project directory: {raw_path}")
    if "images" not in normalized.relative_to(root).parts[:1]:
        raise ValueError(f"image path must live under images/: {raw_path}")
    return normalized


def infer_slide_index(entry: dict, fallback: int) -> int:
    prompt_file = str(entry.get("prompt_file", ""))
    match = re.match(r"prompts/(\d+)-", prompt_file)
    if match:
        return int(match.group(1))
    return fallback


def backend_for(entry: dict, manifest: dict, override: str | None) -> str:
    backend = override or entry.get("backend") or manifest.get("default_backend") or os.environ.get("IMAGE_BACKEND") or "none"
    return str(backend).strip().lower()


def resolve_nanobanana_model() -> str:
    raw = (os.environ.get("NANOBANANA_MODEL") or os.environ.get("GEMINI_MODEL") or NANOBANANA_DEFAULT_MODEL).strip()
    return NANOBANANA_MODEL_ALIASES.get(raw.lower(), raw)


def nanobanana_api_key() -> str:
    return (os.environ.get("NANOBANANA_API_KEY") or os.environ.get("GEMINI_API_KEY") or "").strip()


def gemini_api_key(*, nanobanana: bool) -> str:
    if nanobanana:
        return nanobanana_api_key()
    return (os.environ.get("GEMINI_API_KEY") or "").strip()


def missing_key_for(backend: str) -> str | None:
    if backend == "openai" and not os.environ.get("OPENAI_API_KEY"):
        return "OPENAI_API_KEY"
    if backend == "gemini" and not os.environ.get("GEMINI_API_KEY"):
        return "GEMINI_API_KEY"
    if backend == "nanobanana" and not nanobanana_api_key():
        return "NANOBANANA_API_KEY or GEMINI_API_KEY"
    return None


def selected(entry: dict, entry_number: int, only: set[str]) -> bool:
    if not only:
        return True
    prompt_file = str(entry.get("prompt_file", ""))
    prompt_index = re.match(r"prompts/(\d+)-", prompt_file)
    candidates = {
        str(entry_number),
        f"{entry_number:02d}",
        str(entry.get("slide_id", "")),
        Path(prompt_file).name,
    }
    if prompt_index:
        candidates.add(prompt_index.group(1))
        candidates.add(str(int(prompt_index.group(1))))
    return bool(only & candidates)


def http_json(url: str, payload: dict, headers: dict[str, str], timeout: int) -> dict:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            # Some OpenAI-compatible gateways (e.g. Cloudflare-fronted proxies)
            # block Python's default urllib User-Agent with 403 / error 1010.
            "User-Agent": "ai-slide-producer/generate_images",
            **headers,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {body[:800]}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"request failed: {exc.reason}") from exc


def download_url(url: str, timeout: int) -> bytes:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return response.read()


def openai_payload(prompt: str, aspect_ratio: str, image_size: str) -> tuple[dict, str]:
    model = os.environ.get("OPENAI_MODEL") or "gpt-image-2"
    output_format = (os.environ.get("OPENAI_OUTPUT_FORMAT") or "png").strip().lower()
    if output_format not in {"png", "jpeg", "webp"}:
        raise ValueError("OPENAI_OUTPUT_FORMAT must be png, jpeg, or webp")
    output_ext = ".jpg" if output_format == "jpeg" else f".{output_format}"
    payload = {
        "model": model,
        "prompt": prompt,
        "n": 1,
        "size": OPENAI_SIZES_16_9.get(image_size) if aspect_ratio == "16:9" else OPENAI_SIZE_BY_ASPECT.get(aspect_ratio, "1280x720"),
        "quality": IMAGE_QUALITY.get(image_size, "medium"),
    }
    if model.lower().startswith("gpt-image-"):
        payload["output_format"] = output_format
        compression = os.environ.get("OPENAI_OUTPUT_COMPRESSION")
        if compression:
            payload["output_compression"] = int(compression)
        background = os.environ.get("OPENAI_BACKGROUND")
        if background:
            payload["background"] = background
        moderation = os.environ.get("OPENAI_MODERATION")
        if moderation:
            payload["moderation"] = moderation
    else:
        payload["response_format"] = "b64_json"
    return payload, output_ext


def generate_openai(prompt: str, aspect_ratio: str, image_size: str, timeout: int) -> tuple[bytes, str]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise GenerationSkip("OPENAI_API_KEY is not set")
    base_url = (os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
    url = f"{base_url}/images/generations"
    payload, output_ext = openai_payload(prompt, aspect_ratio, image_size)
    data = http_json(url, payload, {"Authorization": f"Bearer {api_key}"}, timeout)
    images = data.get("data") or []
    if not images:
        raise RuntimeError("OpenAI response did not include image data")
    first = images[0]
    if first.get("b64_json"):
        return base64.b64decode(first["b64_json"]), output_ext
    if first.get("url"):
        return download_url(first["url"], timeout), output_ext
    raise RuntimeError("OpenAI response had neither b64_json nor url")


def gemini_payload(prompt: str, aspect_ratio: str, image_size: str) -> dict:
    return {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {
                "aspectRatio": aspect_ratio,
                "imageSize": image_size,
            },
        },
    }


def generate_gemini(
    prompt: str,
    aspect_ratio: str,
    image_size: str,
    timeout: int,
    *,
    nanobanana: bool = False,
) -> tuple[bytes, str]:
    api_key = gemini_api_key(nanobanana=nanobanana)
    if not api_key:
        if nanobanana:
            raise GenerationSkip("NANOBANANA_API_KEY or GEMINI_API_KEY is not set")
        raise GenerationSkip("GEMINI_API_KEY is not set")
    if nanobanana:
        model = resolve_nanobanana_model()
        base_url = (
            os.environ.get("NANOBANANA_BASE_URL")
            or os.environ.get("GEMINI_BASE_URL")
            or "https://generativelanguage.googleapis.com"
        ).rstrip("/")
    else:
        model = (os.environ.get("GEMINI_MODEL") or NANOBANANA_DEFAULT_MODEL).strip()
        base_url = (os.environ.get("GEMINI_BASE_URL") or "https://generativelanguage.googleapis.com").rstrip("/")
    escaped_model = urllib.parse.quote(model, safe="")
    url = f"{base_url}/v1beta/models/{escaped_model}:generateContent"
    # Prefer header auth (Google AI Studio default); query ?key= remains valid but can hang on some networks.
    data = http_json(
        url,
        gemini_payload(prompt, aspect_ratio, image_size),
        {"X-goog-api-key": api_key},
        timeout,
    )
    parts = []
    for candidate in data.get("candidates") or []:
        content = candidate.get("content") or {}
        parts.extend(content.get("parts") or [])
    for part in reversed(parts):
        inline = part.get("inlineData") or part.get("inline_data")
        if inline and inline.get("data"):
            return base64.b64decode(inline["data"]), ".png"
    raise RuntimeError("Gemini response did not include inline image data")


def generate_bytes(backend: str, prompt: str, aspect_ratio: str, image_size: str, timeout: int) -> tuple[bytes, str]:
    if backend == "openai":
        return generate_openai(prompt, aspect_ratio, image_size, timeout)
    if backend == "gemini":
        return generate_gemini(prompt, aspect_ratio, image_size, timeout, nanobanana=False)
    if backend == "nanobanana":
        return generate_gemini(prompt, aspect_ratio, image_size, timeout, nanobanana=True)
    raise GenerationSkip(f"backend '{backend}' is not implemented by generate_images.py")


def target_path(project_dir: Path, entry: dict, fields: dict[str, str], index: int, output_ext: str) -> Path:
    raw_path = entry.get("image_file") or fields.get("generated_image_path") or f"images/slide-{index:02d}.png"
    path = safe_project_path(project_dir, str(raw_path), default=f"images/slide-{index:02d}.png")
    if output_ext and path.suffix.lower() != output_ext:
        path = path.with_suffix(output_ext)
    return path


def run(project_dir: Path, args: argparse.Namespace) -> int:
    skill_root = args.skill_root.resolve()
    load_env(project_dir, skill_root)
    manifest_path = project_dir / "images_manifest.json"
    manifest = load_json(manifest_path)
    entries = manifest.get("entries")
    if not isinstance(entries, list):
        raise SystemExit("images_manifest.json entries must be an array")

    only = {token.strip() for token in (args.only or "").split(",") if token.strip()}
    image_size = args.image_size
    touched = False
    summary = {"generated": 0, "skipped": 0, "manual": 0, "dry_run": 0}

    for entry_number, entry in enumerate(entries, start=1):
        if not selected(entry, entry_number, only):
            continue
        slide_id = entry.get("slide_id", f"entry-{entry_number}")
        backend = backend_for(entry, manifest, args.backend)
        if backend in PASSIVE_BACKENDS:
            print(f"warning: {slide_id}: backend '{backend}' has no active generator; keeping pending", file=sys.stderr)
            summary["skipped"] += 1
            continue
        if backend not in SUPPORTED_BACKENDS:
            print(f"warning: {slide_id}: unsupported backend '{backend}'; keeping pending", file=sys.stderr)
            summary["skipped"] += 1
            continue
        missing_key = missing_key_for(backend)
        if missing_key:
            print(f"warning: {slide_id}: {missing_key} is not set; keeping pending", file=sys.stderr)
            summary["skipped"] += 1
            continue
        status = entry.get("status", "pending")
        if status == "ok" and not args.force:
            print(f"skip: {slide_id}: status ok")
            summary["skipped"] += 1
            continue
        if status not in PROCESSABLE_STATUSES and not args.force:
            print(f"skip: {slide_id}: status {status}")
            summary["skipped"] += 1
            continue
        prompt_path = project_dir / str(entry.get("prompt_file", ""))
        if not prompt_path.exists():
            entry["status"] = "needs-manual"
            entry["error_message"] = f"missing prompt file: {entry.get('prompt_file')}"
            entry["updated_at"] = now_iso()
            touched = True
            summary["manual"] += 1
            continue

        fields, prompt = prompt_parts(prompt_path)
        if not prompt:
            entry["status"] = "needs-manual"
            entry["error_message"] = f"empty prompt body: {entry.get('prompt_file')}"
            entry["updated_at"] = now_iso()
            touched = True
            summary["manual"] += 1
            continue

        slide_index = infer_slide_index(entry, entry_number)
        aspect_ratio = entry.get("aspect_ratio") or fields.get("target_aspect_ratio") or manifest.get("default_aspect_ratio") or "16:9"
        expected_path = target_path(project_dir, entry, fields, slide_index, ".png")
        if expected_path.exists() and not args.force:
            entry["status"] = "ok"
            entry["image_file"] = str(expected_path.relative_to(project_dir))
            entry.pop("error_message", None)
            entry["updated_at"] = now_iso()
            touched = True
            print(f"ok: {slide_id}: existing image {entry['image_file']}")
            summary["skipped"] += 1
            continue

        if args.dry_run:
            print(f"dry-run: {slide_id}: {backend} -> {expected_path.relative_to(project_dir)}")
            summary["dry_run"] += 1
            continue

        try:
            entry["status"] = "generating"
            entry["backend"] = backend
            entry["attempts"] = int(entry.get("attempts") or 0) + 1
            entry["updated_at"] = now_iso()
            save_json(manifest_path, manifest)
            image_data, output_ext = generate_bytes(backend, prompt, str(aspect_ratio), image_size, args.timeout)
            image_path = target_path(project_dir, entry, fields, slide_index, output_ext)
            image_path.parent.mkdir(parents=True, exist_ok=True)
            image_path.write_bytes(image_data)
            entry["status"] = "ok"
            entry["image_file"] = str(image_path.relative_to(project_dir))
            entry["updated_at"] = now_iso()
            entry.pop("error_message", None)
            touched = True
            summary["generated"] += 1
            print(f"generated: {slide_id}: {entry['image_file']}")
            if args.sleep > 0:
                time.sleep(args.sleep)
        except GenerationSkip as exc:
            entry["status"] = "pending"
            entry["updated_at"] = now_iso()
            entry["error_message"] = str(exc)
            touched = True
            summary["skipped"] += 1
            print(f"warning: {slide_id}: {exc}; keeping pending", file=sys.stderr)
        except Exception as exc:
            entry["status"] = "needs-manual"
            entry["updated_at"] = now_iso()
            entry["error_message"] = str(exc)
            touched = True
            summary["manual"] += 1
            print(f"error: {slide_id}: {exc}; marked needs-manual", file=sys.stderr)
        finally:
            if touched:
                save_json(manifest_path, manifest)

    if not args.dry_run and touched:
        manifest["updated_at"] = now_iso()
        save_json(manifest_path, manifest)
    print(
        "image generation summary: "
        f"generated={summary['generated']}, skipped={summary['skipped']}, "
        f"needs_manual={summary['manual']}, dry_run={summary['dry_run']}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", type=Path)
    parser.add_argument("--skill-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--backend", choices=sorted(SUPPORTED_BACKENDS | PASSIVE_BACKENDS), default=None)
    parser.add_argument("--only", help="comma-separated slide ids, 1-based indexes, or prompt filenames")
    parser.add_argument("--force", action="store_true", help="regenerate even when manifest status is ok or an image exists")
    parser.add_argument("--dry-run", action="store_true", help="show what would be generated without changing files")
    parser.add_argument("--image-size", choices=["512px", "1K", "2K", "4K"], default="1K")
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--sleep", type=float, default=0.0, help="seconds to wait between successful generations")
    args = parser.parse_args()

    return run(args.project_dir.resolve(), args)


if __name__ == "__main__":
    raise SystemExit(main())
