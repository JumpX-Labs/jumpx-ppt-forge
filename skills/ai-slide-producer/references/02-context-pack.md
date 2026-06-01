# 02 — Context Pack

> Step 2 落地文档。把 Brief + 用户材料压缩成固定结构，选定视觉风格，并固化输出形态决议。

---

## 角色

> 切换到 **Strategist + Researcher**。

职责：

- Strategist：从 Brief 推 Narrative Direction / Design Direction。
- Researcher：从用户材料抽取 Knowledge Base / Key Claims，过滤冗余。
- 共同输出 `context_pack.md`，作为后续 Outline / Slide Plan / Design Spec 的单一信源。

---

## 输出结构（固定字段）

落盘到 `<project>/source/context_pack.md`。**字段名稳定**，值可用任意语言。

```markdown
# Context Pack

**Created**: YYYY-MM-DD HH:mm
**Source Brief**: project_brief.md
**Style Preset**: <kebab-case 标识，例 teaching-clean>
**Output Mode**: <image-first | html-only | html-takeover | mixed | html-only-with-prompts>

---

## Project Goal
<1–2 句话，本 deck 要让受众发生什么转变。不是主题，是"目标"。>

## Audience
- Primary: <主要受众 + 知识水平>
- Secondary: <次要受众，如有>
- Pain / Curiosity / Decision context: <受众此刻关心什么>

## Use Case
- Scene: <演讲 / 教学 / 阅读 / 汇报 / 传播 / ...>
- Format: <现场 / 录播 / 异步阅读 / 社群发图 / ...>
- Recommended output: <见 §场景 → 形态推荐表>

## Knowledge Base
- Source 1: <名称 + 性质 + 长度 + 摘要 1 段>
- Source 2: ...
- Coverage gaps: <发现的明显空缺；可由 AI 补 or 用户补>

## Key Claims
- <可被引用的核心主张 1>
- <核心主张 2>
- ...

## Narrative Direction
- Arc: <Hook→Context→Core→Shift→Takeaway | 教学六段 | 商业六段 | 产品六段 | 咨询六段 | 自定义>
- Tone: <严谨 / 故事 / 教学 / 营销 / 学术 / 实操>
- Pacing: <平均每页一个 idea | 大密度 | 节奏感强>

## Design Direction
- Style Preset: <见 §Preset 一对一映射表>
- Reason for preset: <为什么选这个 preset，1–2 句>
- Visual mood: <2–3 个形容词>
- Density: <high | medium-high | medium | medium-low | low>

## Tone Rules
- Voice: <第一人称 we / 中性 / ...>
- Avoid: <避免的措辞，例 "dive into", "let's explore"，AI 味的话>
- Prefer: <鼓励的措辞>

## Forbidden Zones
- <Hard constraint 1，来自 Brief 第 8 问>
- <内容禁区 2>
- ...

## Acceptance Criteria
- Result must include: <交付硬性要求>
- Quality bar: <用户的"够不够好"标准>

## Output Mode
- Decision: <见上方头部，重复一次以便机器解析>
- Backend probe result: <available | unavailable + 理由>
- Takeover note (if any): <告诉用户的话>
```

---

## 7 套风格怎么选

完整说明见 [`12-style-presets.md`](12-style-presets.md)。Step 2 只需在 Context Pack 里定下 `style_name` 与理由；Step 6 再写入 `style_lock.json`。

| Preset（id） | 展示名 | 适用场景 |
|--------------|--------|----------|
| `teaching-clean` | Teaching Clean | 教学课件、概念讲解、清楚留白 |
| `swiss-system` | Swiss System | 咨询汇报、技术路线、信息密集 |
| `editorial-magazine` | Editorial Magazine | 对外展示、强叙事、演讲开场 |
| `blueprint` | Blueprint | 产品发布、系统架构、蓝图风 |
| `sketch-notes` | Sketch Notes | 手绘感、社群传播、轻松分享 |
| `corporate` | Corporate | 商务汇报、稳重克制 |
| `creator-social` | Creator Social | 个人 IP、社媒轮播 |

**资产位置**：网页样式 → `assets/styles/<preset>.css`；出图描述 → `assets/style-presets/<preset>.json`。

---

## 场景 → 输出形态建议

| 场景 | 推荐形态 | 备选 |
|------|---------|------|
| 教学课件 | HTML | 封面 + 金句页用 Image |
| 现场演讲 | HTML | 关键章节页用 Image |
| 商业汇报 | HTML | 全套 |
| 社群传播 | Image | HTML 作完整版备份 |
| 阅读自解释 | Image 或 Mixed | — |
| 公开发布 / 媒体投放 | Image | — |
| 内部讨论 / 草稿 | HTML | — |
| 个人作品集 | Mixed | — |

**注**：推荐≠强制。Intake 第 7 问最终采纳用户选择；本表只在用户犹豫时用来给建议。

---

## 输出形态探测细则

**触发时机**：Step 1 收尾，Brief 落盘前。

**落盘时机**：Step 1 只写入 `project_brief.md` § Output Mode；Step 2 生成 `context_pack.md` 时复制该决议，不重新探测，除非用户在 Gate 1 明确更改输出偏好或 backend 配置。

**探测顺序（级联探测，优先级从高到低）**：

1. **Step A: 用户指令覆盖**：若用户显式指定了形态（如 `Web` / `html-only`，或在对话中指定可用 backend），以用户结论为准。**若用户指定为 Web，最终形态为 `html-only`**，有 Key 也不覆盖。
2. **Step B: Runtime 原生工具检测**：优先检查 runtime 原生图像生成工具（如 `imagegen`, `image_generate`, `mcp__*__image_*`）是否可用。
3. **Step C: 本地探测脚本检测**：在 `<skill-root>` 运行 `python3 scripts/probe_image_backend.py <project-dir>`。**由于 CraftAgents 等 GUI 客户端沙箱可能会过滤敏感环境变量，Agent 禁止只靠进程环境变量检测，必须尝试在终端跑探测脚本。**
   - 脚本检测本地与全局 `~/.ai-slide-producer/.env`。
   - 成功时将脚本探测明细写入 `project_brief.md`。
4. **Step D: Agent 进程环境检测（兜底）**：仅在脚本执行因环境受限失败时作为兜底，检查 Agent 自身进程环境变量。
5. 都不存在且无用户指定 → backend 不可用，staged prompt manifests 使用 `default_backend: "none"`。

**决议矩阵**（与 SKILL.md 一致，再录一次便于查阅）：

| 用户偏好（问题 7） | Backend | Output Mode |
|-------------------|---------|-------------|
| `image` 或未指定 | available | `image-first` |
| `image` 或未指定 | unavailable | `html-takeover`（7A-P：仍导出 Prompts） |
| `web` | — | `html-only` |
| `mixed` | available | `mixed` |
| `mixed` | unavailable | `html-only-with-prompts`（7A-P：仅为需配图页落 Prompt） |

**写入处**：

1. `project_brief.md` § Output Mode（详细，含探测理由）
2. `context_pack.md` 头部 `Output Mode:` 行 + § Output Mode 段（精简）
3. Step 7 入口的 GATE 条件（决定走 7A / 7B / 二者）

**告知用户**：仅当结果为 `html-takeover` 或 `html-only-with-prompts` 时，在 Round 1 确认里**明示**。其他情况静默。

---

## Knowledge Base 整理纪律

Researcher 处理用户材料时遵守：

- **不直接读图**：用户提供图片材料时，请用户描述或让 AI 转写为文本要点；不要把图片二进制塞进 Prompt。
- **去重**：Source 1 与 Source 2 同一论点只在 `## Key Claims` 出现一次。
- **过滤可疑事实**：未经验证的数字、引语标 `[unverified]`，Step 5 Reviewer 会复核。
- **保留可引用原话**：用户原话中的精彩短句单独列在 `## Key Claims`，加引号；后续 Writer 可直接引用。

---

## 与其他角色的衔接

| 下一步 | 谁接手 | 用到本阶段的什么 |
|--------|--------|------------------|
| Step 3 Outline | Strategist | `Narrative Direction.Arc` 直接套用；`Audience` 决定知识起点 |
| Step 4 Slide Plan | Writer | `Key Claims` 是每页 `key_message` 的池；`Tone Rules` 控制 `on_slide_text` 措辞 |
| Step 6 Design Spec | Designer | `Design Direction.Style Preset` 直接写入 `style_lock.json.style_name`；`Density` 写 `style_lock.json.density` |
| Step 7 Render | Renderer | `Output Mode` 决定路径；`Forbidden Zones` 写入 `style_lock.json.forbidden[]` |

---

**关联文档**：
- [`12-style-presets.md`](12-style-presets.md) — 风格细则
- [`00-product-principles.md`](00-product-principles.md)
- [`01-intake-brief.md`](01-intake-brief.md) — 上一步
- [`../schemas/style_lock.schema.json`](../schemas/style_lock.schema.json) — Style Lock 字段
