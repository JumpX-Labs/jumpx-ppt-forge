#!/usr/bin/env python3
"""Validate generated AI Slide Producer HTML — deterministic Tier-0 QA.

Pure Python stdlib. No browser, no network → runs in any agent / cloud sandbox.
This is the *measured* half of Step 8 QA: it turns checks the model used to judge
by eye (color drift, layout/page-id consistency, external resources, text budgets)
into a hard machine verdict, so the regeneration loop can CONVERGE instead of
flip-flopping on subjective re-reads.

What it CAN measure here (Tier 0):
  - structure contract (#deck / .slide / controls / ESC index / inline script)
  - residual {{placeholders}}
  - external resources (禁外链 / self-contained contract)
  - page-id + layout consistency vs slide_plan.json (catches regeneration drift)
  - style_lock colors actually used + conservative "foreign color" drift
  - rough text-budget overflow proxy per layout

What it CANNOT measure here (needs the optional Tier-1 render check in the shell,
e.g. Playwright): real rendered pixel overflow (getBoundingClientRect) and WCAG
contrast. Those stay optional/detected so the skill itself keeps zero deps.

Usage:
  validate_html.py index.html
  validate_html.py index.html --style-lock source/style_lock.json \
                              --slide-plan source/slide_plan.json
  validate_html.py index.html --style-lock ... --json
  validate_html.py index.html --strict   # warnings become failures
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

PLACEHOLDER_RE = re.compile(r"{{\s*[a-zA-Z0-9_]+\s*}}")
HEX_RE = re.compile(r"#[0-9A-Fa-f]{3,8}\b")
# External resource = anything pulled over the network. Contract = self-contained / all-inline.
EXTERNAL_RE = re.compile(
    r"""(?ix)
    (?:
        <link\b[^>]*\bhref\s*=\s*['"]https?:// |    # <link href="http...">
        @import\b[^;]*url\(\s*['"]?https?:// |        # @import url(http...)
        \bsrc\s*=\s*['"]https?:// |                  # src="http..." (script/img/iframe)
        \burl\(\s*['"]?https?:// |                    # background:url(http...)
        fonts\.googleapis\.com | fonts\.gstatic\.com  # web font CDNs
    )
    """
)

# Per-layout "body item" soft budgets (mirror references/10-style-guard.md 溢出风险).
LAYOUT_BUDGET = {
    "comparison": 4,
    "timeline": 6,
    "framework": 6,
    "closing": 6,
    "_default": 6,
}


# --------------------------------------------------------------------------- #
# HTML parsing
# --------------------------------------------------------------------------- #
class SlideParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.sections: list[dict] = []  # {page_id, layout, li, text}
        self.has_deck = False
        self.has_controls = False
        self.has_index = False
        self.scripts = 0
        self._depth = 0
        self._cur: dict | None = None
        self._cur_depth = 0

    def handle_starttag(self, tag, attrs):
        data = {k: (v or "") for k, v in attrs}
        self._depth += 1
        if tag == "main" and data.get("id") == "deck":
            self.has_deck = True
        if tag == "nav" and "slide-controls" in data.get("class", "").split():
            self.has_controls = True
        if tag == "div" and data.get("id") == "index":
            self.has_index = True
        if tag == "script":
            self.scripts += 1
        if tag == "section" and "slide" in data.get("class", "").split():
            self._cur = {
                "page_id": data.get("data-page-id", ""),
                "layout": data.get("data-layout", ""),
                "li": 0,
                "text": "",
            }
            self._cur_depth = self._depth
            self.sections.append(self._cur)
        if self._cur is not None and tag == "li":
            self._cur["li"] += 1

    def handle_endtag(self, tag):
        if self._cur is not None and tag == "section" and self._depth == self._cur_depth:
            self._cur = None
        self._depth -= 1

    def handle_data(self, data):
        if self._cur is not None:
            self._cur["text"] += data


# --------------------------------------------------------------------------- #
# color helpers
# --------------------------------------------------------------------------- #
def _norm_hex(h: str) -> str:
    h = h.lstrip("#").lower()
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return h[:6]  # drop alpha


def _hex_to_hsl(h: str) -> tuple[float, float, float]:
    h = _norm_hex(h)
    if len(h) < 6:
        return 0.0, 0.0, 0.0
    r, g, b = (int(h[i : i + 2], 16) / 255 for i in (0, 2, 4))
    mx, mn = max(r, g, b), min(r, g, b)
    light = (mx + mn) / 2
    if mx == mn:
        return 0.0, 0.0, light
    d = mx - mn
    sat = d / (2 - mx - mn) if light > 0.5 else d / (mx + mn)
    if mx == r:
        hue = (g - b) / d + (6 if g < b else 0)
    elif mx == g:
        hue = (b - r) / d + 2
    else:
        hue = (r - g) / d + 4
    return hue * 60, sat, light


def _hue_dist(a: float, b: float) -> float:
    d = abs(a - b) % 360
    return min(d, 360 - d)


# --------------------------------------------------------------------------- #
# loaders
# --------------------------------------------------------------------------- #
def _load_json(path: Path | None):
    if not path:
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return {"__error__": str(e)}


def _lock_hexes(lock: dict) -> list[str]:
    keys = (
        "primary_color",
        "accent_color",
        "background_color",
        "text_primary_color",
        "text_secondary_color",
        "border_color",
    )
    out = [lock[k] for k in keys if isinstance(lock.get(k), str) and lock[k].startswith("#")]
    for c in lock.get("color_palette", []) or []:
        if isinstance(c, dict) and isinstance(c.get("hex"), str):
            out.append(c["hex"])
    return [_norm_hex(h) for h in out]


# --------------------------------------------------------------------------- #
# main validation
# --------------------------------------------------------------------------- #
def validate(html_path: Path, lock: dict | None, plan: dict | None) -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    try:
        text = html_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {"ok": False, "errors": [f"missing html: {html_path}"], "warnings": [], "pages": []}

    # ---- placeholders & structure ----
    if PLACEHOLDER_RE.search(text):
        errors.append("residual {{placeholder}} found")
    if "<script>alert" in text.lower():
        warnings.append("possible unescaped script-looking text found")

    p = SlideParser()
    p.feed(text)
    if not p.has_deck:
        errors.append("missing main#deck")
    if not p.sections:
        errors.append("no .slide sections found")
    if not p.has_controls:
        errors.append("missing .slide-controls")
    if not p.has_index:
        errors.append("missing ESC index container (#index)")
    if p.scripts == 0:
        errors.append("missing inline slide script")

    # ---- external resources (self-contained contract) ----
    ext = EXTERNAL_RE.findall(text)
    if ext:
        m = EXTERNAL_RE.search(text)
        snippet = (m.group(0)[:60].replace("\n", " ") if m else "")
        errors.append(f"external resource (违反自包含/禁外链契约): …{snippet}… [{len(ext)} total]")

    # ---- page-id + layout consistency ----
    plan_pages = (plan or {}).get("pages") if isinstance(plan, dict) else None
    html_ids = [s["page_id"] for s in p.sections]
    if len(html_ids) != len(set(html_ids)):
        errors.append(f"duplicate data-page-id in HTML: {html_ids}")

    if plan_pages:
        total = ((plan or {}).get("deck_meta") or {}).get("total_pages")
        if isinstance(total, int) and total != len(p.sections):
            errors.append(f"section count {len(p.sections)} ≠ deck_meta.total_pages {total}")
        plan_ids = [pg.get("page_id", "") for pg in plan_pages]
        plan_layouts = [pg.get("layout_type", "") for pg in plan_pages]
        if html_ids != plan_ids:
            errors.append(f"page-id order mismatch vs slide_plan: html={html_ids} plan={plan_ids}")
        for i, sec in enumerate(p.sections):
            if i < len(plan_layouts) and sec["layout"] and plan_layouts[i] and sec["layout"] != plan_layouts[i]:
                warnings.append(
                    f"{sec['page_id'] or f'section {i+1}'}: data-layout='{sec['layout']}' "
                    f"≠ slide_plan layout_type='{plan_layouts[i]}'"
                )
    else:
        # no plan → positional P0N sequence, but actionable
        for i, pid in enumerate(html_ids, start=1):
            exp = f"P{i:02d}"
            if pid != exp:
                errors.append(f"section {i}: data-page-id='{pid}' should be '{exp}' (P01,P02,… in order)")

    # ---- text-budget overflow proxy (rough; real check is Tier-1 render) ----
    pages_report = []
    for i, sec in enumerate(p.sections, start=1):
        budget = LAYOUT_BUDGET.get(sec["layout"], LAYOUT_BUDGET["_default"])
        if sec["li"] > budget:
            warnings.append(
                f"{sec['page_id'] or f'section {i}'}: {sec['li']} list items > {budget} "
                f"budget for layout '{sec['layout'] or 'generic'}' (overflow risk)"
            )
        chars = len(re.sub(r"\s+", "", sec["text"]))
        if chars > 420:
            warnings.append(
                f"{sec['page_id'] or f'section {i}'}: ~{chars} visible chars (dense; verify no overflow)"
            )
        pages_report.append(
            {"page_id": sec["page_id"], "layout": sec["layout"], "li": sec["li"], "chars": chars}
        )

    # ---- color: lock usage + conservative foreign-color drift ----
    if isinstance(lock, dict) and "__error__" not in lock:
        lock_set = set(_lock_hexes(lock))
        html_hexes = {_norm_hex(h) for h in HEX_RE.findall(text)}
        for key in ("primary_color", "accent_color", "background_color"):
            v = lock.get(key)
            if isinstance(v, str) and v.startswith("#") and _norm_hex(v) not in html_hexes:
                warnings.append(f"style_lock.{key} {v} not found in HTML (lock may be ignored)")
        lock_hues = [_hex_to_hsl(h)[0] for h in lock_set if _hex_to_hsl(h)[1] > 0.15]
        foreign = []
        for hx in html_hexes - lock_set:
            hue, sat, light = _hex_to_hsl(hx)
            if sat < 0.30 or light < 0.12 or light > 0.92:
                continue  # neutral / near-black / near-white → derived, fine
            if lock_hues and min(_hue_dist(hue, lh) for lh in lock_hues) <= 22:
                continue  # tint/shade of a lock hue → fine
            foreign.append(f"#{hx}")
        if foreign:
            warnings.append(
                "possible foreign colors (not in style_lock; confirm intentional — "
                f"status/derived ok): {', '.join(sorted(set(foreign))[:8])}"
            )
    elif isinstance(lock, dict) and "__error__" in lock:
        warnings.append(f"could not read style_lock: {lock['__error__']}")

    return {"ok": not errors, "errors": errors, "warnings": warnings, "pages": pages_report}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("html", type=Path)
    ap.add_argument("--style-lock", type=Path, default=None, help="source/style_lock.json (enables color/drift checks)")
    ap.add_argument("--slide-plan", type=Path, default=None, help="source/slide_plan.json (enables count/layout cross-check)")
    ap.add_argument("--json", action="store_true", help="machine-readable verdict (for the regeneration loop / shell)")
    ap.add_argument("--strict", action="store_true", help="treat warnings as failures")
    a = ap.parse_args()

    lock = _load_json(a.style_lock)
    plan = _load_json(a.slide_plan)
    res = validate(a.html.resolve(), lock, plan)

    failed = bool(res["errors"]) or (a.strict and bool(res["warnings"]))

    if a.json:
        res["strict"] = a.strict
        res["failed"] = failed
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 1 if failed else 0

    for w in res["warnings"]:
        print(f"warning: {w}", file=sys.stderr)
    for e in res["errors"]:
        print(f"error: {e}", file=sys.stderr)
    if failed:
        return 1
    print(f"html ok: {a.html}  ({len(res['pages'])} slides, {len(res['warnings'])} warning(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
