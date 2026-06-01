# Context Pack

**Style Preset**: editorial-magazine
**Output Mode**: html-only

## Project Goal

Create a browser-openable sample deck that proves the editorial-magazine preset raises visual quality without changing the renderer contract.

## Audience

- Primary: product reviewers deciding whether the preset meets the visual bar.
- Secondary: implementers who need a compact regression sample.

## Narrative Direction

- Arc: Hook -> Problem -> Upgrade -> Evidence -> Takeaway
- Tone: confident, product-facing, concise.

## Design Direction

- Style Preset: editorial-magazine
- Reason: product feedback called the current teaching-clean demo too plain for outward-facing demos.
- Visual mood: magazine, high contrast, warm paper, strong typographic rhythm.

## Acceptance Criteria

- HTML builds from `source/slide_plan.json` + `source/style_lock.json`.
- Browser output feels visibly different from `teaching-clean`.
- Comparison page renders four panels.
