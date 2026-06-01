# 13 — Regeneration Workflow

> Step 7C 中间态续生与局部重生。目标是只动目标页，保留可审计备份，不伪造图片。

---

## 角色

> 切换到 **Producer / Regeneration Operator**。

职责：

- 根据用户指定的页码或 `page_id` 标记局部重生。
- 备份旧 Prompt / 图片资产。
- 更新 `images_manifest.json` 状态。
- 需要时调 `generate_images.py` 出图；HTML 由 Web Renderer（模型）按 08 契约重写相关页。

---

## CLI

```bash
python3 scripts/regenerate_slide.py <project-dir> P03
python3 scripts/regenerate_slide.py <project-dir> 3,5
python3 scripts/regenerate_slide.py <project-dir> P03 --generate --backend openai
python3 scripts/regenerate_slide.py <project-dir> P03 --mode prompts-only --no-build-html
```

Selectors 支持：

- `P03`
- `3` / `03`
- prompt 文件名，如 `03-slide-context-pack.md`
- 逗号分隔的多个 selector

---

## 模式

| Mode | 行为 |
|------|------|
| `images-only` | 默认。复制旧 Prompt 备份，移动旧图片到备份，manifest 标记 `regenerate-requested` |
| `prompts-only` | 只备份 Prompt 并标记，保留旧图片 |
| `full` | 备份 Prompt，移动旧图片，供后续 Prompt 调整 + 图片重生 |

默认不调用图片 backend。只有传 `--generate` 才会调用：

```bash
python3 scripts/generate_images.py <project-dir> --only P03 --force
```

出图/标记完成后，由 Web Renderer（模型）按 [`08-web-renderer.md`](08-web-renderer.md) 重写受影响页的 `<section>`（或整本 `index.html`）。

---

## 状态流转

```text
ok / pending / failed / needs-manual
        ↓ regenerate_slide.py
regenerate-requested
        ↓ generate_images.py --force（backend 可用）
ok
        ↓ backend 错误
needs-manual
```

无 key 或 backend 不可用时，不生成占位图；`generate_images.py` 保持 `pending` 或 warning，HTML 路径继续可交付。

---

## 备份规则

备份目录：

```text
backups/regenerate-YYYYMMDD-HHMMSS/
├── prompts/...
└── images/...
```

规则：

- Prompt 默认 copy 备份，原文件保留，方便人工编辑后继续生成。
- 图片默认 move 备份，避免 `generate_images.py` 把旧图误判为成功产物。
- 传 `--keep-old-image` 时图片 copy 备份且原图保留。
- 每次执行追加 `source/regeneration_log.md`。

---

## 验收

- 只更新 selector 命中的 manifest entries。
- 目标页状态变为 `regenerate-requested`。
- 目标页旧图被备份，且不再作为当前 `image_file`。
- 非目标页 Prompt / 图片 / manifest 状态不变。
- `index.html` 可重建，目标页无图时显示 HTML fallback。
