# 07 — Designer

> Step 6 落地文档。把内容计划转成 `design_spec.md` 与 `style_lock.json`。

---

## 角色

> 切换到 **Deck Designer**。

职责：

- 根据 `context_pack.md` 的 Design Direction 生成可执行风格系统。
- 写人类可读 `source/design_spec.md`。
- 写机器可读 `source/style_lock.json`，并通过 `schemas/style_lock.schema.json`。
- Gate 4 前向用户呈现风格摘要。

---

## 输入

- `source/context_pack.md`
- `source/slide_plan.json`
- `assets/style-presets/<style_name>.json`
- `schemas/style_lock.schema.json`

---

## Style Lock 生成规则

- `style_name` 必须等于 `slide_plan.deck_meta.style_name`。
- 颜色、字体、密度、图像风格优先来自 `assets/style-presets/<style_name>.json`。
- **`forbidden[]` 必须并入**三处来源：① preset 的 `negative_constraints`（**必填，不是"可选追加"**）② Context Pack 的 Forbidden Zones ③ 用户硬约束。
  > ⚠️ 这条是硬规则：preset 里写的"反廉价感"约束（如 `no decorative gradients as the main visual`、`no faux 3D business clipart`、`no unreadable small labels`、`no crowded text blocks`）**只有进了 `forbidden[]` 才会被渲染器（08）看到**——`style_lock` 是 08 唯一的视觉真相源，08 不读 preset。漏掉这步＝整套反约束在 HTML 主路径上失效。
- Gate 4 通过后，`style_lock.json` 只读；如用户改风格，走 regenerate 流程。

---

## `teaching-clean` 参考默认值

未从 `assets/style-presets/` 覆盖时，`teaching-clean` 可使用：

| 字段 | 默认值 |
|------|--------|
| `primary_color` | `#111827` |
| `accent_color` | `#2563EB` |
| `background_color` | `#F8FAFC` |
| `font_heading` | `Inter, "Noto Sans SC", sans-serif` |
| `font_body` | `Inter, "Noto Sans SC", sans-serif` |
| `image_style` | `clean educational diagram, simple geometric illustration, soft editorial screenshots` |
| `density` | `medium-low` |
| `layout_bias` | `grid` |

---

## `design_spec.md` 模板

```markdown
# Design Spec

**Style Preset**: teaching-clean
**Source Plan**: slide_plan.json
**Lock File**: style_lock.json

## Visual Intent
<这套视觉为何适合该受众和场景>

## Canvas
- Ratio: 16:9
- Recommended pixels: 1920 x 1080

## Color System
- Background: <hex>
- Primary text: <hex>
- Accent: <hex>
- Supporting colors: <list>

## Typography
- Heading: <font stack>
- Body: <font stack>
- Rule: no viewport-scaled font sizes in compact UI; slide type scale comes from CSS tokens.

## Layout Rules
- One main idea per page.
- Use whitespace as a teaching device.
- Prefer diagrams, comparisons, and process steps over long prose.

## Image Strategy
<when to use generated images or placeholders>

## Forbidden
- <hard rule>
```

---

## Gate 4 摘要格式

向用户展示：

- Style Preset
- 3 个核心色值
- 字体系统
- 页面密度
- 图片策略
- 任何 forbidden 约束

用户确认后才能进入 Step 7。

