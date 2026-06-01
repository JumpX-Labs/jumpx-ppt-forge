# 00 — Product Principles

> 本 Skill 的 8 条产品原则与可执行规则。所有角色文件引用本文件，作为设计决策的最终仲裁。

---

## P1 — 最终结果优先

**原则**：系统的最终交付不能只是建议、大纲、文案、Prompt 或 Markdown，必须包含至少一种可见交付。

**可执行规则**：

- 任意流程跑到 Step 9 时，`<project>/` 下必须存在以下三者之一：
  - `index.html`（可双击打开）
  - `images/slide-NN.png`（至少 1 张）
  - `<project>.pptx` / `<project>.pdf`（后续版本可选，当前 Skill 不生成）
- 仅有 `outline.md`、`slide_plan.json`、`prompts/` 不算完成交付。
- 例外：用户显式请求中间态（`outline-only` / `prompts-only`）时，按用户请求停在该层，但 `qa_report.md` 必须说明"已按中间态请求停在 X"。

**违反信号**：用户问"在哪能看到结果"时若答不上来——重看本条。

---

## P2 — 先确认，再放大

**原则**：四个关键节点必须停下等用户确认，避免长流程返工。

**可执行规则**（与 SKILL.md Gate 1/2/4/5 对齐）：

| 时机 | 不确认就禁止下一步 |
|------|--------------------|
| Brief 未确认 | 不进入 Outline |
| Outline 未确认 | 不进入逐页内容生成 |
| 风格未冻结 | 不进入批量视觉生产（Image / HTML 渲染） |
| Style Guard 未通过 | 不进入 Delivery |

**违反信号**：在用户没回话时，AI 自作主张连推到下一阶段。

---

## P3 — 流程可见，角色清楚

**原则**：用户不必理解所有细节，但系统内部任何时刻都必须能回答：当前在哪一步、由谁负责、本步输入/输出、是否需要用户确认。

**可执行规则**：

- 每次大动作前，单句报告"现在做 X（Step N，角色：Y）"。
- 状态机字段（见 SKILL.md §状态机）必须随中间产物落盘——Agent 读 `<project>/source/` 任意一个文件就能反推当前进度。
- 角色切换在 reference 文件中用 `> 切换到 <Role>` 起首段标记。

---

## P4 — Context Lock 防漂移

**原则**：一旦冻结，不重写不漂移。

**可执行规则**：

- 以下字段在 Gate 4 通过后写入 `style_lock.json`，整个后续流程**只读不改**（除非走显式 regenerate 流程并更新 lock）：
  - `deck_title` / `audience` / `canvas_ratio`
  - `style_name` / `primary_color` / `accent_color` / `background_color`
  - `font_heading` / `font_body`
  - `image_style` / `density`
  - `forbidden[]`
- Web Renderer 每渲染一页、Image Renderer 每生成一页 Prompt，必须**重读** `style_lock.json`，禁止从对话历史里拷贝色值/字体。
- 用户改风格 → 走 regenerate 流程更新 lock + 涉及页重生，不要做"打补丁"。

---

## P5 — Image-first，HTML 自动接管

**原则**：未指定输出时走 Image；backend 不可用时自动切 HTML，且保留 Prompts。

**可执行规则**：

- Output Mode 探测时机固定在 Step 1 Intake 收尾（见 SKILL.md §Output Mode 探测时机）。
- 切换到 HTML 不算"降级"，HTML 是一等输出形态。
- 切换时必须告知用户："当前无可用图片 backend，已切到 HTML 路径，Image Prompts 仍会落盘待生。"
- HTML takeover 路径仍按 `slide_plan.json` 的 `image_requirement` 字段进入 Step 7A-P Prompt Staging，准备 `prompts/NN-*.md` 与 `images_manifest.json`，但不调用 backend。

---

## P6 — 输出形态不绑定消费场景

**原则**：系统不假设 HTML 一定演讲、Image 一定传播、PPT 一定汇报。

**可执行规则**：

- Intake 第 1 问问"消费场景"（演讲 / 教学 / 社群传播 / 阅读 / 商业汇报 / …），第 7 问问"输出形态"（HTML / Image / Mixed），二者独立采集。
- 可基于场景**推荐**输出形态（见 `02-context-pack.md` §场景 → 形态推荐），但必须允许用户覆盖；用户选定后写入 `context_pack.md` `Output Mode` 字段，不再改动。

---

## P7 — Prompt Archive 是核心资产

**原则**：图片是结果，Prompt 是资产。

**可执行规则**（对 Image 路径）：

- 每页 Prompt 必须单独落盘为 `prompts/NN-slide-{slug}.md`，schema 见 [`../schemas/image_prompts.schema.json`](../schemas/image_prompts.schema.json)。
- Prompt 文件必须先于 backend 调用存在。
- 字段至少包括：`slide_id`、`slide_title`、`visible_text`、`visual_composition`、`style_preset`、`style_lock_ref`、`negative_constraints`、`target_aspect_ratio`、`image_backend`、`generated_image_path`。
- 整个 deck 必须有一份 `images_manifest.json` 汇总（schema 同上文件）。
- 切换 backend / 重生页面时只改 manifest 状态字段，不删 Prompt 文件。

---

## P8 — 支持中间态输出

**原则**：不强制一次跑完，让系统可编辑、可复用、可局部返工。

**可执行规则**：

- 5 种中间态模式（详见 SKILL.md §Step 7C）：`outline-only` / `prompts-only` / `images-only` / `html-only` / `regenerate <pages>`。
- 中间态停下时，仍必须按 P1 给用户可见产物（即使只是"截至本阶段的中间产物清单 + 下一步建议"）。
- 中间态进入时，前置中间产物（如 `outline.md`、`slide_plan.json`）必须已就绪；不存在时报错引导用户先跑前置步骤，禁止边读边猜。

---

## 元规则：原则冲突时的优先级

当原则之间出现张力时（罕见但会发生）：

1. **P1（结果可见）> P2（先确认）**：在中间态下，"先给用户看到的中间产物"比"再确认一遍"更重要。
2. **P4（Lock 防漂移）> P5（自动接管）**：自动切 HTML 时不准顺手改 `style_lock.json`——只在 `context_pack.md` 的 Output Mode 字段记。
3. **P7（Prompt 资产）> 效率**：哪怕用户催促"直接出图"，也必须先落 Prompt 再调 API。这是产品价值的根。

---

**关联文档**：
- [`SKILL.md`](../SKILL.md) — 管线铁律
- [`01-intake-brief.md`](01-intake-brief.md) — P3/P5/P6 在 Intake 的落地
- [`02-context-pack.md`](02-context-pack.md) — P4/P5/P6 在 Context Pack 的落地
- [`15-export-contract.md`](15-export-contract.md) — P1/P7/P8 在交付的落地
