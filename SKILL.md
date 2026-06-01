---
name: ai-slide-producer
description: >
  AI Slides 生产器。把主题、资料、想法变成可打开的 HTML 幻灯片或可查看的 Image Slides。
  Image-first，HTML 自动接管。一体化主 Skill，内部多角色、多门禁、双输出路径。
  Use when user says "做一份 PPT", "做一个 deck", "做几页 slides", "生成课件",
  "做汇报", "做产品发布材料", "做演讲 slides", "把这份资料变成 PPT", "make a slide deck",
  "make a presentation", or asks to turn material into slides for teaching / sharing /
  pitching / publishing.
---

# AI Slide Producer

> 一句话定义：把粗糙输入变成**可见 Slides 结果**的 AI 生产系统——Image 与 HTML 双输出，每一步都有人工门禁，每页 Prompt 都是可复用资产。

**主管线**：`Intake → Context Pack → Outline → Slide Plan → Narrative Review → Design Spec → Render (Image / HTML) → Quality Check → Delivery`

---

> [!CAUTION]
> ## 🚨 管线铁律（MANDATORY）
>
> **本 Skill 是严格串行管线。以下规则优先级最高，违反任一条等同执行失败：**
>
> 1. **SERIAL EXECUTION** — 步骤必须按序执行，上一步输出是下一步输入。非 ⛔BLOCKING 的相邻步骤在前置满足后可连续推进，无需等"继续"指令。
> 2. **BLOCKING = HARD STOP** — 标 ⛔BLOCKING 的步骤必须完全停下，等待用户明确响应，不得替用户决定。
> 3. **NO CROSS-PHASE BUNDLING** — 禁止跨阶段打包。Gate 1/2/4 是 ⛔BLOCKING；一旦用户在某 Gate 确认，后续非 BLOCKING 步骤可自动连推到下一 Gate。
> 4. **GATE BEFORE ENTRY** — 每个 Step 顶部列出 🚧GATE 前置条件，必须先验证再进入。
> 5. **NO SPECULATIVE EXECUTION** — 禁止预先生成后续步骤产物（例如 Strategist 阶段写 Slide Plan、Outline 阶段画 HTML）。
> 6. **STYLE LOCK RE-READ PER PAGE** — 进入 Step 7A/7B 后，每页 Image Prompt 或 HTML section 生成前，必须重读 `style_lock.json`。所有 color / font / image_style / density 值必须来自该文件，不得凭记忆或临时发明。本规则用于抵抗长 deck 的上下文压缩漂移。
> 7. **IMAGE PATH 禁止伪造** — 若用户选择 Image 路径，必须调用真实图片生成 backend；禁止用 HTML、SVG、Canvas、代码渲染冒充 raster image。Backend 不可用时按 §Output Mode 自动切 HTML，并进入 Prompt Staging 保留完整 Image Prompts。
> 8. **PROMPT 先落盘再调 API** — 每页 Image Prompt 必须先写入 `prompts/NN-slide-{slug}.md`，再调用图片 backend。Prompt 是资产，图片是结果。
> 9. **REVIEWER 自动 1 轮限制** — Step 5 Reviewer 自动触发；若返工，最多自动重写 1 轮；超过 1 轮回退到 Gate 2（大纲确认）由用户重审，禁止无限自动重写。

---

> [!IMPORTANT]
> ## 🌐 Language & Communication Rule
>
> - **响应语言**：匹配用户输入与源材料的主语言。用户显式指定（例如"请用英文回答"）优先。
> - **中间产物**：所有 `*.md` / `*.json` 字段名沿用 schema 英文键，**值**使用用户语言。
> - **图片 Prompt**：图像模型不擅长非英语长描述。中文叙事 deck 的视觉描述（Composition / Visual hierarchy / Style notes）默认双语，可见文本（Visible text）保持原语言。

---

## 触发与参数提取

### 触发关键词

`description` 字段已包含中英文常用触发；典型场景：

- 做一份 PPT / 做一个 deck / 做几页 slides
- 生成课件 / 做汇报 / 做演讲 slides
- 做产品发布材料 / 把这份资料变成 PPT
- make a slide deck / make a presentation

### Agent 调度时的参数提取顺序

| 顺位 | 参数 | 默认值 / 来源 |
|------|------|--------------|
| 1 | 主题（必需） | 用户输入；缺失则在 Intake 第 1 问询问 |
| 2 | 受众 | 可推断；不确定时 Intake 第 2 问询问 |
| 3 | 页数 | 默认 8–12；按 Outline 长度自调 |
| 4 | 风格 | 默认 `teaching-clean` |
| 5 | 输出形态 | 默认 Image-first（HTML 自动接管，见下方 Output Mode） |
| 6 | 特殊约束 | 可推断；显式提及的禁区写入 `forbidden[]` |

---

## 状态机（对外可被 Agent 查询）

```
brief → outline → plan → review → spec → render → qa → delivery
```

每个状态对应一份中间产物，详见 [`references/15-export-contract.md`](references/15-export-contract.md)：

| 状态 | 主要产物 | 写入路径 |
|------|----------|----------|
| brief | `project_brief.md` | `<project>/source/` |
| outline | `outline.md` | `<project>/source/` |
| plan | `slide_plan.json` | `<project>/source/` |
| review | `review_report.md` | `<project>/source/` |
| spec | `design_spec.md` + `style_lock.json` | `<project>/source/` |
| render | `index.html` 和/或 `images/slide-NN.png` + `prompts/` | `<project>/` |
| qa | `qa_report.md` | `<project>/` |
| delivery | 完整目录树（见 `15-export-contract.md`） | `<project>/` |

Agent 可读任意中间产物判断当前进度并决定下一步动作。

---

## 输出形态（Output Mode）探测

**何时探测**：Step 1 需求澄清收尾时（用户确认 Brief 前）一次性完成，结果先写入 `project_brief.md` 的 `Output Mode` 字段；Step 2 再复制到 `context_pack.md`。不要等到 Step 7 才发现出图服务不可用。

**探测流程**：

1. 读用户在 Intake 的输出形态偏好（Image / Web / Mixed / 未指定）。
2. 检测当前 runtime 的图片生成能力（Cascading 级联探测流程）：
   - **Step A: 用户指令覆盖（最高优先级）**：若用户在对话或指令中显式指定了形态偏好（如指定了 `Web` 或 `html-only`，或在对话中指明可用 backend），直接采用用户指定结论。**注意：若第 7 问指定为 Web，最终模式必须为 `html-only`，即使本地有可用 backend 也不改写为 `image-first`（backend 可用性仅作记录）。**
   - **Step B: Runtime 原生工具检测**：优先检查 runtime 是否有原生图像生成 tool（如 `imagegen`、`image_generate`、`mcp__*__image_*`）。
   - **Step C: 本地探测脚本检测**：若无原生工具，尝试在 `<skill-root>` 执行以下命令探测本地/全局 `.env` 配置：
     ```bash
     python3 scripts/probe_image_backend.py <project-dir>
     ```
     以脚本输出 JSON 的可用状态（如 `{"openai": {"available": true}}`）为准判定。**对于 CraftAgents 等 GUI 客户端沙箱环境，由于敏感进程环境变量常被过滤，必须尝试在终端跑本脚本，禁止只靠 Step D 判定。**探测成功后将脚本输出的探测明细写入 `project_brief.md`。
   - **Step D: Agent 进程环境变量检测（兜底）**：仅在脚本执行因环境受限失败时，兜底检查 Agent 进程是否含 `OPENAI_API_KEY`、`NANOBANANA_API_KEY` 或 `GEMINI_API_KEY`（见 `.env.example`）。
   - 都不存在且无用户指明 → backend 不可用。
3. 决议矩阵：

| 用户偏好 | 出图服务可用 | 最终模式（id） | 用户会看到什么 |
|----------|-------------|----------------|----------------|
| 要图片 / 未指定 | ✅ | `image-first` | 每页一张 PNG，可配网页版 |
| 要图片 / 未指定 | ❌ | `html-takeover` | 改为网页版；图片 Prompt 仍会保存，便于以后出图 |
| 只要网页 | — | `html-only` | 可本地打开的 HTML 幻灯片 |
| 网页 + 部分配图 | ✅ | `mixed` | HTML 为主，指定页用配图 |
| 网页 + 部分配图 | ❌ | `html-only-with-prompts` | 先出网页；封面/金句等页的 Prompt 已写好，待有 Key 再出图 |

4. `html-takeover` 与 `html-only-with-prompts` 必须在 Brief 确认时**显式告知用户**："当前无可用图片 backend，已自动切换到 HTML 路径，Image Prompts 仍会落盘以便后续生成。"

---

## Workflow（九步主流程）

### Step 1：Intake / 需求澄清

> 详见 [`references/01-intake-brief.md`](references/01-intake-brief.md)

**🚧 GATE**：用户提供主题/资料/想法（任一即可）。

**做什么**：

- 按 8 问清单澄清关键变量（场景、受众、时长、页数、已有材料、风格、输出形态、硬约束）。
- 收尾时执行 Output Mode 探测。
- 输出 `project_brief.md`。

**⛔ BLOCKING — Gate 1 Brief Confirmed**：必须呈现 Brief 摘要 + Output Mode 决议，等待用户明确确认（"OK / 改 X"）后才能进入 Step 2。

---

### Step 2：Context Pack / 上下文资产包

> 详见 [`references/02-context-pack.md`](references/02-context-pack.md)

**🚧 GATE**：Gate 1 通过。

**做什么**：

- 将 Brief + 用户材料压缩为固定结构（Project Goal / Audience / Use Case / Knowledge Base / Narrative Direction / Design Direction / Tone Rules / Forbidden Zones / Acceptance Criteria / Output Mode）。
- 根据场景 + 内容信号选定 Style Preset（见 `02-context-pack.md` §Preset 映射表）。
- 输出 `context_pack.md`。

**呈现摘要**给用户（非 BLOCKING）；用户无异议则继续。

---

### Step 3：Outline / 叙事大纲

> 详见 [`references/03-strategist.md`](references/03-strategist.md)

**🚧 GATE**：`context_pack.md` 存在。

**做什么**：

- 切换到 Deck Strategist，基于 Context Pack 生成大纲。
- 默认结构：`Hook → Context → Core → Shift → Takeaway`。
- 按场景切换：
  - 教学课件：问题 → 概念 → 方法 → 示例 → 练习 → 总结
  - 商业汇报：背景 → 问题 → 洞察 → 方案 → 路径 → 决策
  - 产品发布：痛点 → 新机会 → 产品 → 价值 → Demo → 行动
  - 咨询方案：现状 → 诊断 → 框架 → 建议 → 路线图 → 风险
- 输出 `outline.md`（含叙事策略、每页一句话定位、总页数）。
- 禁止在本阶段写 `slide_plan.json` 或 `index.html`。

**⛔ BLOCKING — Gate 2 Outline Confirmed**：必须等用户确认章节顺序、页数、叙事主线。

---

### Step 4：Slide Plan / 页面计划

> 详见 [`references/04-researcher.md`](references/04-researcher.md) 与 [`references/05-writer.md`](references/05-writer.md)

**🚧 GATE**：Gate 2 通过。

**做什么**：

- Researcher 先整理 Claim Bank、Page Evidence Map 与事实风险；可输出 `research_notes.md`。
- Writer 将大纲转为逐页计划，每页字段见 [`schemas/slide_plan.schema.json`](schemas/slide_plan.schema.json)：
  `page_id` / `page_title` / `page_goal` / `page_role_in_story` / `key_message` / `on_slide_text` / `speaker_notes` / `visual_direction` / `layout_type` / `image_requirement`。
- 输出 `slide_plan.json`（首选；必须符合 schema）。
- 通过 schema 结构检查后自动进入 Step 5（非 BLOCKING）。
- 本步只产出 `slide_plan.json`，**不在此处写 HTML**（HTML 是 Step 7B 的事；铁律 5 禁止预先生成后续产物）。

---

### Step 5：Narrative Review / 内容审核

> 详见 [`references/06-reviewer.md`](references/06-reviewer.md)

**🚧 GATE**：`slide_plan.json` 存在且通过结构检查。

**做什么**：Reviewer **自动触发**，无需用户启动。

- 检查主线完整性、每页独立功能、衔接、重复、遗漏、受众匹配、事实风险、过度承诺。
- 输出 `review_report.md`。

**返工策略**：

| 严重度 | 处理 |
|--------|------|
| 无 issue | 进入 Step 6 |
| 仅 warning | 在 `review_report.md` 标注，进入 Step 6 |
| 1 处 critical | 按 [`references/05-writer.md`](references/05-writer.md) 返工策略，Writer 自动重写涉及页 + Slide Plan 增量更新 + Reviewer 再跑一轮 |
| 2+ critical **或** 自动重写仍未通过 | **回退到 Gate 2（Outline）** 由用户重审，禁止继续自动重写 |

---

### Step 6：Design Spec & Style Lock / 视觉规格

> 详见 [`references/07-designer.md`](references/07-designer.md)

**🚧 GATE**：Step 5 通过（无未解决 critical）。

**做什么**：

- 写人类可读的 `design_spec.md`（叙事 + 设计意图）。
- 写机器执行的 `style_lock.json`，字段见 [`schemas/style_lock.schema.json`](schemas/style_lock.schema.json)：
  `deck_title` / `audience` / `canvas_ratio` / `style_name` / `primary_color` / `accent_color` / `background_color` / `font_heading` / `font_body` / `image_style` / `density` / `forbidden[]`。

**⛔ BLOCKING — Gate 4 Style Locked**：必须等用户确认风格、色彩、字体、图片策略、页面密度后才进入 Step 7。

> Gate 3（Content Approved）由 Step 5 Reviewer 自动跑出，不阻塞用户；只有 critical 才阻塞。

---

### Step 7A：Image Prompt Staging & Render / 图片 Prompt 落盘与生成

> 详见 [`references/09-image-renderer.md`](references/09-image-renderer.md)

**🚧 GATE**：Gate 4 通过 **且** Output Mode ∈ {`image-first`, `mixed`, `html-takeover`, `html-only-with-prompts`}，或用户显式请求 `prompts-only`。

**做什么**：

**准备图片 Prompt**（适用于 `image-first` / `mixed` / `html-takeover` / `html-only-with-prompts` / `prompts-only`）

1. **逐页**派生 Image Prompt（每页生成前重读 `style_lock.json`）。
2. Prompt 先写入 `prompts/NN-slide-{slug}.md`（schema 见 [`schemas/image_prompts.schema.json`](schemas/image_prompts.schema.json)）。
3. 写入 `images_manifest.json`（每页 prompt 路径、目标图片路径、backend、状态、aspect ratio）。
4. 当 Output Mode 为 `html-takeover` / `html-only-with-prompts` / `prompts-only` 时，manifest 条目保持 `status: pending`，不调用 backend。

**调用出图服务**（仅适用于 `image-first` / `mixed` 且出图服务可用）

1. 从已落盘的 `prompts/` 与 `images_manifest.json` 读取待生成条目。
2. **先向用户说明耗时预期**（见 [`references/09-image-renderer.md`](references/09-image-renderer.md) §生成耗时预期）：同步 API 约 **60–90 秒/页**，串行累加；4 页约 4–6 分钟。
3. 调用图片 backend 生成 `images/slide-NN.png`（本机执行 `generate_images.py`，非对话内瞬时完成）。
4. 回写 `images_manifest.json` 状态与错误信息。

**硬规则**：禁止 SVG/HTML/Canvas 伪装；禁止用代码在 bitmap 上修字。Backend 失败 → 标记 `status: needs-manual`，继续后续页，最后在 `qa_report.md` 汇总。

### Step 7B：Web Render / HTML 生成

> 详见 [`references/08-web-renderer.md`](references/08-web-renderer.md)

**🚧 GATE**：Gate 4 通过 **且** Output Mode ∈ {`html-only`, `html-takeover`, `mixed`, `html-only-with-prompts`}。

**做什么**（主路径 = 模型直接写 HTML；脚本模板为回退。细则见 [`references/08-web-renderer.md`](references/08-web-renderer.md)）：

- **主路径**：由你（模型）按 `slide_plan.json` + `style_lock.json`（设计 token）**直接编写 `index.html`**，每页根据内容与角色自由做版面设计，达到专业水准。必须遵守 08 文档的**硬契约**（`#deck` + 每页 `<section class="slide">` 100vw、`translateX` 翻页、自包含、不溢出）与 `style_lock.forbidden`。
- **回退路径**：需纯脚本可复现 / 批量 / 无人值守时，用 `scripts/build_html.py`（模板片段拼装，质量受模板封顶）。
- Mixed 项目必须在配图生成完成（或本地已有 `images/slide-NN.*`）后再渲染。
- 单页 HTML，16:9 画布，横向翻页（键盘 ←→、指示器、ESC 缩略图、移动端滑动）；CSS 内联，本地可直接打开。
- 输出 `index.html`，跑 `scripts/validate_html.py` 校验。

### Step 7C：Intermediate Output / 中间态

通过 CLI 参数或对话指令支持：

| 模式 | 含义 |
|------|------|
| `outline-only` | 停在 Step 3 之后 |
| `prompts-only` | 只导出图片 Prompt（7A-P），不调出图 API |
| `images-only` | 跳过 Step 1–6，从已有 `prompts/` 生成图片 |
| `html-only` | 跳过 Step 7A，只跑 Step 7B |
| `regenerate <N>` 或 `regenerate <N>,<M>,<K>` | 局部重生指定页 |

详见 [`references/13-regeneration-workflow.md`](references/13-regeneration-workflow.md)。

---

### Step 8：Quality Check / 质量检查

> 总表见 [`references/14-quality-checklist.md`](references/14-quality-checklist.md)，视觉守门见 [`references/10-style-guard.md`](references/10-style-guard.md)

**🚧 GATE**：Step 7 至少有一个 render 路径完成。

**做什么**：

- **Reviewer 内容复检**：主线、每页独立作用、标题表达力、事实风险。
- **Style Guard 视觉检查**（[`references/10-style-guard.md`](references/10-style-guard.md)）：颜色 / 字体 / 版式漂移、文本溢出、视觉拥挤、图片契约。
- **Producer 交付检查**：HTML 可打开、图片齐全、文件命名规范、manifest 存在。
- 输出 `qa_report.md`。

**⛔ Gate 5 Style Compliance**：严重漂移必须返工（按 §13 regeneration 流程局部重生）。

---

### Step 9：Delivery / 交付

> 交付树见 [`references/15-export-contract.md`](references/15-export-contract.md)，Producer 执行规则见 [`references/11-producer.md`](references/11-producer.md)

**🚧 GATE**：Step 8 通过。

**做什么**：

- 按 [`references/15-export-contract.md`](references/15-export-contract.md) 定义的目录树组织文件。
- 写 `README.md`（项目层）说明：怎么打开、怎么改、怎么重生。
- 按 [`references/11-producer.md`](references/11-producer.md) 复核 Output Mode、可见产物和 Gate 6。
- 给用户**可见结果链接 / 路径**（HTML 文件或图片目录）。

**Gate 6 Result Visible**：交付前必须确认用户可获得至少一种可见产物（可打开的 HTML、可查看的图片、或两者）。

---

## 本 Skill 目录结构

```
skills/ai-slide-producer/
├── SKILL.md                 # 总入口（本文件）
├── .env.example             # 出图 API 环境变量模板
├── references/              # 各步骤角色手册（00–15）；索引见 references/README.md
├── schemas/                 # slide_plan / style_lock / image_prompts
├── assets/
│   ├── templates/           # HTML 模板与 layout 片段
│   ├── styles/              # 7 套风格的网页 CSS
│   ├── style-presets/       # 7 套风格的出图描述 JSON
│   └── examples/            # 可打开的样例 deck
└── scripts/                 # 探测、出图、拼装 HTML、校验等
```

**能力说明**：完整九步管线；支持 `html-only` / `image-first` / `mixed` 等输出形态；出图 backend 可选 `openai`、`nanobanana`（Gemini Image）、`gemini`（legacy id）。维护与回归文档见 `docs/`（Agent 日常不必读）。

---

## 7 套视觉风格（Preset）

选型细则见 [`references/12-style-presets.md`](references/12-style-presets.md)。简表：

| Preset（id） | 一句话 | 适合 |
|--------------|--------|------|
| `teaching-clean` | 清楚、留白、教学友好 | 训练营课件、概念讲解 |
| `editorial-magazine` | 杂志感、大标题、强叙事 | 对外展示、演讲开场 |
| `swiss-system` | 网格、理性、信息密集 | 咨询汇报、技术路线 |
| `blueprint` | 蓝图、架构感 | 产品/系统方案 |
| `sketch-notes` | 手绘、轻松 | 社群分享、工作坊 |
| `corporate` | 稳重商务 | 企业汇报、提案 |
| `creator-social` | 轻量、社媒节奏 | 个人 IP、轮播 |

---

## 版权说明

本 Skill 内置模板与风格资产来自多个开源样本；拷贝代码时需保留各文件中的版权头。**最终交付给用户的 deck 目录中不写这些说明。**

---

**Skill 版本**：v1.0
