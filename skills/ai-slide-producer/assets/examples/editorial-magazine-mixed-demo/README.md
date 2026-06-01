# Editorial Magazine Mixed Demo

Editorial Magazine **Mixed** sample. Proves the HTML deck can embed local slide images from `images/slide-NN.png`.

---

## How To View

- Open `index.html` in a browser.
- Use keyboard left/right arrows to navigate.
- P04 and P07 should show local embedded images.

## Included

- Output Mode: `mixed`
- Style Preset: `editorial-magazine`
- HTML: yes
- Images: 2 placeholder PNGs
- QA: `qa_report.md`

## How To Rebuild

From `skills/ai-slide-producer/`:

```bash
python3 scripts/build_html.py assets/examples/editorial-magazine-mixed-demo
python3 scripts/validate_html.py assets/examples/editorial-magazine-mixed-demo/index.html
```

## Known Issues

- Placeholder PNGs are intentionally simple repository assets, not API-generated production images.
