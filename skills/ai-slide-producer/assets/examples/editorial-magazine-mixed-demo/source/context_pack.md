# Context Pack

**Style Preset**: editorial-magazine
**Output Mode**: mixed

## Project Goal

Create a browser-openable sample deck that proves HTML can embed local slide images in an HTML deck without changing the renderer contract.

## Audience

- Primary: product reviewers deciding whether Mixed output bar is met.
- Secondary: implementers who need a compact regression sample.

## Narrative Direction

- Arc: Hook -> Problem -> Upgrade -> Evidence -> Takeaway
- Tone: confident, product-facing, concise.

## Design Direction

- Style Preset: editorial-magazine
- Reason: mixed output needs a product-facing visual sample while keeping HTML readable.
- Visual mood: magazine, high contrast, warm paper, strong typographic rhythm.

## Acceptance Criteria

- HTML builds from `source/slide_plan.json` + `source/style_lock.json`.
- Browser output embeds at least two local `images/slide-NN.png` files.
- Missing images degrade to an explicit pending state.
