# Editorial Magazine Image-first Demo

Image-first acceptance sample for `editorial-magazine`. Placeholder PNGs are committed so UAT does not require API quota.

## How To View

- Primary artifact: `images/slide-01.png` through `images/slide-05.png`.
- Backup HTML: open `index.html`.

## Real Backend Smoke

Configure `.env`, then run:

```bash
python3 scripts/generate_images.py assets/examples/editorial-magazine-image-first-demo --backend openai --only P01
```

Expect roughly 60-90 seconds per page for real image generation. Do not commit API-generated large images.
