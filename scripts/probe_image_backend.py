#!/usr/bin/env python3
"""Lightweight script to detect image generation backend API keys and test connection.

Reuses load_env from generate_images.py to resolve the exact same environment variables.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

# Add parent directory of this script to python path to import load_env
script_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(script_dir))

try:
    from generate_images import load_env, nanobanana_api_key, resolve_nanobanana_model
except ImportError:
    nanobanana_api_key = None  # type: ignore
    resolve_nanobanana_model = None  # type: ignore
    # Minimal fallback in case we cannot import generate_images
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
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            if not any(key.startswith(p) for p in ("IMAGE_", "OPENAI_", "GEMINI_", "NANOBANANA_")):
                continue
            val = value.strip().strip("'").strip('"')
            os.environ.setdefault(key, val)
        return env_path


def test_openai_connection(api_key: str, base_url: str, timeout: int) -> tuple[bool, str | None]:
    url = f"{base_url.rstrip('/')}/models"
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "ai-slide-producer/probe_backend",
        },
        method="GET"
    )
    primary_error = None
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if response.status == 200:
                return True, None
            primary_error = f"HTTP status {response.status}"
    except urllib.error.HTTPError as exc:
        if exc.code == 401:
            return False, f"HTTP status 401 Unauthorized"
        primary_error = f"HTTP status {exc.code} {exc.msg}"
    except Exception as exc:
        primary_error = str(exc)

    # Fallback dry-run to /images/generations for compatible gateways that disable /models
    images_url = f"{base_url.rstrip('/')}/images/generations"
    payload = json.dumps({"prompt": ""}).encode("utf-8")
    fallback_request = urllib.request.Request(
        images_url,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ai-slide-producer/probe_backend",
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(fallback_request, timeout=timeout) as response:
            if response.status == 200:
                return True, None
    except urllib.error.HTTPError as exc:
        # A 400 Bad Request indicating invalid parameters (such as empty prompt)
        # means the API key was valid and the request hit the actual generation backend.
        if exc.code == 400:
            try:
                body = exc.read().decode("utf-8", errors="replace")
                err_data = json.loads(body)
                err_msg = err_data.get("error", {}).get("message", "")
                err_code = err_data.get("error", {}).get("code", "")
                if "api_key" in err_code or "invalid_api_key" in err_msg or "Incorrect API key" in err_msg:
                    return False, f"Auth failed on fallback: {err_msg or err_code}"
            except Exception:
                pass
            return True, None
        return False, f"Primary error: {primary_error}; Fallback error: HTTP status {exc.code} {exc.msg}"
    except Exception as exc:
        return False, f"Primary error: {primary_error}; Fallback error: {exc}"


def test_gemini_connection(api_key: str, base_url: str, timeout: int) -> tuple[bool, str | None]:
    url = f"{base_url.rstrip('/')}/v1beta/models"
    request = urllib.request.Request(
        url,
        headers={
            "X-goog-api-key": api_key,
            "User-Agent": "ai-slide-producer/probe_backend",
        },
        method="GET"
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if response.status == 200:
                return True, None
            return False, f"HTTP status {response.status}"
    except Exception as exc:
        return False, str(exc)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", type=Path, nargs="?", default=Path.cwd())
    parser.add_argument("--skill-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--test-connection", action="store_true", help="perform dry-run HTTP requests to verify backend credentials")
    parser.add_argument("--timeout", type=int, default=10, help="timeout in seconds for connection test")
    args = parser.parse_args()

    project_dir = args.project_dir.resolve()
    skill_root = args.skill_root.resolve()

    # Load environment variables using the shared logic
    loaded_path = load_env(project_dir, skill_root)

    openai_key = os.environ.get("OPENAI_API_KEY", "").strip()
    gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
    nano_key = nanobanana_api_key() if nanobanana_api_key else (
        (os.environ.get("NANOBANANA_API_KEY") or os.environ.get("GEMINI_API_KEY") or "").strip()
    )

    openai_available = bool(openai_key)
    gemini_available = bool(gemini_key)
    nanobanana_available = bool(nano_key)

    result: dict[str, Any] = {
        "openai": {
            "available": openai_available,
        },
        "gemini": {
            "available": gemini_available,
        },
        "nanobanana": {
            "available": nanobanana_available,
            "provider": "google-gemini-image-api",
        },
        "loaded_env_from": str(loaded_path) if loaded_path else None
    }

    # Add models info if configured
    if openai_available:
        result["openai"]["model"] = os.environ.get("OPENAI_MODEL", "gpt-image-2")
    if gemini_available:
        result["gemini"]["model"] = os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-image-preview")
    if nanobanana_available:
        if resolve_nanobanana_model:
            result["nanobanana"]["model"] = resolve_nanobanana_model()
        else:
            result["nanobanana"]["model"] = os.environ.get(
                "NANOBANANA_MODEL", os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-image-preview")
            )

    # Determine recommended backend
    active_backend = os.environ.get("IMAGE_BACKEND", "").strip().lower()
    availability = {
        "openai": openai_available,
        "gemini": gemini_available,
        "nanobanana": nanobanana_available,
    }
    if active_backend in availability:
        result["recommended"] = active_backend if availability[active_backend] else "none"
    elif openai_available:
        result["recommended"] = "openai"
    elif nanobanana_available:
        result["recommended"] = "nanobanana"
    elif gemini_available:
        result["recommended"] = "gemini"
    else:
        result["recommended"] = "none"

    # Connection testing if requested
    connection_failed = False
    if args.test_connection:
        if openai_available:
            base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
            connected, err = test_openai_connection(openai_key, base_url, args.timeout)
            result["openai"]["connected"] = connected
            result["openai"]["connection_error"] = err
            if not connected:
                connection_failed = True
        else:
            result["openai"]["connected"] = False
            result["openai"]["connection_error"] = None

        if gemini_available:
            base_url = os.environ.get("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com")
            connected, err = test_gemini_connection(gemini_key, base_url, args.timeout)
            result["gemini"]["connected"] = connected
            result["gemini"]["connection_error"] = err
            if not connected:
                connection_failed = True
        else:
            result["gemini"]["connected"] = False
            result["gemini"]["connection_error"] = None

        if nanobanana_available:
            base_url = (
                os.environ.get("NANOBANANA_BASE_URL")
                or os.environ.get("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com")
            )
            connected, err = test_gemini_connection(nano_key, base_url, args.timeout)
            result["nanobanana"]["connected"] = connected
            result["nanobanana"]["connection_error"] = err
            if not connected:
                connection_failed = True
        else:
            result["nanobanana"]["connected"] = False
            result["nanobanana"]["connection_error"] = None

    # Print JSON output to stdout
    print(json.dumps(result, indent=2))

    if args.test_connection and connection_failed:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
