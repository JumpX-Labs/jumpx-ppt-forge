# 01 — Intake / Brief

> Step 1 落地文档。澄清→落盘→门禁。

---

## 角色

> 切换到 **Intake Facilitator**（兼 Strategist 前置）。

职责：

- 用最少的问题获取最大的信息密度。
- 不要把"应该由 AI 推断的"问题甩给用户。
- 把模糊偏好转成可记录的字段。

---

## 8 问清单

按顺序问；用户已答的不再追问；多个问题可在一段话里合并。

| # | 问题 | 必需 / 可推断 | 默认 / 提示 |
|---|------|---------------|-------------|
| 1 | 这份 slides 的**消费场景**是什么？ | 必需 | 演讲 / 教学课件 / 社群分享 / 阅读自解释 / 商业汇报 / 内部讨论 / 公开发布 / 个人作品集 |
| 2 | **受众**是谁？知识程度大概什么水平？ | 可推断 | 例：高校学生 / 行业从业者 / 投资人 / 客户决策层 / 普通公众 |
| 3 | 希望讲/读**多长时间**？ | 可推断 | 影响页数：5 分钟约 5–8 页，15 分钟约 12–20 页，30 分钟约 25–40 页 |
| 4 | 预计**多少页**？ | 可推断 | 默认 8–12；用户给了时长就按时长估 |
| 5 | 你已有的**材料**是什么？（文字/链接/笔记/草稿/纯主题） | 必需 | 列出每件材料的形式与长度 |
| 6 | 想要什么**风格**？ | 可推断 | 默认 `teaching-clean`；展示 7 套 preset 简称让用户挑或描述偏好 |
| 7 | 最终想要 **Web / Image / Mixed**？ | 可推断 | 默认 Image-first；未指定时按 §Output Mode 探测决议 |
| 8 | 有没有**必须出现 / 不能出现**的内容？ | 可推断 | 例：必须含某 case；不要提某竞品；不要超过某结论 |

---

## Round 1 确认（一次性校对）

收齐 8 项后，向用户呈现以下结构（不要分散追问；要一次性显示让用户校对）：

```
## 已经确认的设定
- **场景**：<答案 1>
- **受众**：<答案 2>
- **时长 / 页数**：<答案 3> / <答案 4>
- **已有材料**：<答案 5 摘要，列名+长度+性质>
- **风格**：<答案 6，对应 preset → style_name>
- **输出形态**：<答案 7，已含 Output Mode 探测结果>
- **图片耗时预期**（仅 image-first / mixed 且 backend 可用）：约 <N> 页需出图 → 预计 <总分钟数>（按 60–90 秒/页串行估算；本机脚本生成，非对话瞬时）
- **硬约束**：<答案 8>

## 我做出的推断（请校对）
- <每一条 AI 推断的项目，注明依据>

## 接下来我会
1. 整理 Context Pack（Step 2）
2. 产出 Outline（Step 3）—— 这一步会再次停下来确认

确认无误请回 "OK"；想改任意一项请直接说"改 X：..."。
```

**⛔ BLOCKING — Gate 1**：未收到用户确认前不进入 Step 2。

---

## 输出形态探测（与 SKILL.md 一致）

在第 7 问回答收齐后、Round 1 确认呈现前执行：

1. 读问题 7 答案：用户偏好（Image / Web / Mixed / 未指定）。
2. 检测图片 backend（使用级联探测流程，优先级从高到低）：
   - **Step A: 用户指令覆盖（最高优先级）**：若用户显式指定了形态偏好（如指定了 `Web` 或 `html-only`，或在对话中指明可用 backend），直接采用用户指定结论。注意：**如果用户在第 7 问已指定为 Web，则最终形态必须为 `html-only`，即使本地有可用 backend 也不强行改成 image-first，backend 可用性仅作记录。**
   - **Step B: Runtime 原生工具检测**：优先检查 runtime 是否有原生图像生成 tool（如 `imagegen`、`image_generate`、`mcp__*__image_*`）。
   - **Step C: 本地探测脚本检测**：由于 GUI 客户端（如 CraftAgents）沙箱可能隔离或过滤敏感进程环境变量，Agent 必须尝试在本地执行以下命令来读取 `.env` 配置（支持全局 `~/.ai-slide-producer/.env`）：
     ```bash
     python3 scripts/probe_image_backend.py <project-dir>
     ```
     以脚本输出的 JSON 可用状态为准判定。探测成功时，将脚本输出的探测明细写入 `project_brief.md`。
   - **Step D: Agent 进程环境变量检测（兜底）**：若脚本执行因环境受限失败，最后兜底检查 Agent 进程自身的环境变量是否含 `OPENAI_API_KEY` 或 `GEMINI_API_KEY`。
   - 都不存在且无用户指定 → backend 不可用。
3. 按 SKILL.md §Output Mode 决议矩阵给出结果。
4. 在 Round 1 确认里**显示**最终 Output Mode，以及（如有）"自动切换 HTML"的说明。
5. 若最终模式为 `image-first` 或 `mixed` 且 backend **available**，在 Round 1 增加 **图片生成耗时预期**（见 [`09-image-renderer.md`](09-image-renderer.md) §生成耗时预期），按预估页数 × 60–90 秒/页给出总等待时间，避免用户以为对话内秒出图。
6. 将探测结果写入 `project_brief.md` § Output Mode；Step 2 再复制到 `context_pack.md` 头部与 § Output Mode。

---

## 输出物：`project_brief.md`

落盘到 `<project>/source/project_brief.md`。模板：

```markdown
# Project Brief

**Created**: YYYY-MM-DD HH:mm
**Status**: confirmed | draft

## Topic
<一句话主题>

## Use Case
<场景，来自问题 1>

## Audience
<受众，来自问题 2>

## Duration & Page Count
- Duration: <时长>
- Page count: <页数>（如有上下限注明）

## Source Materials
- <材料 1 名称>（形式：md / link / paste / file 引用）
- <材料 2 ...>

## Style Preference
- Preset: <style_name，例 `teaching-clean`>
- Reason: <选这个 preset 的依据；如用户描述 → AI 选择，注明>

## Output Mode
- User preference: <image | web | mixed | unspecified>
- Backend availability: <available | unavailable>
- Final mode: <image-first | html-only | html-takeover | mixed | html-only-with-prompts>
- Note (if takeover): <告诉用户的话>
- Generation time estimate (if image-first / mixed + backend available): <N slides to render> × ~60–90s ≈ <minutes> (serial sync API; run via generate_images.py on user machine)

## Constraints
- Must include: <...>
- Must NOT include: <...>
- Other hard rules: <...>

## Confirmation Trail
- <YYYY-MM-DD HH:mm> User confirmed via "<原话>"
```

---

## 用户输入很粗糙时怎么办

允许用户只说"帮我做一份 AI 课程的 PPT"。处理：

1. 不要一次问 8 个问题。先**预填 AI 推断 + 默认值**，再让用户校对。
2. 显示预填版 Round 1 确认，让用户改。
3. 用户改一项 → 重新呈现修订版，不要追加新问题。
4. 三轮还没收敛 → 切到极简模式：只确认场景、页数、输出形态三项，其余按默认推进，并告诉用户"我会按默认推进，你看到 Outline 时还能再调整。"

**反例**（禁止）：

- ❌ 一次甩 8 个问号给用户
- ❌ 用户答完后还在追加细枝末节的问题
- ❌ 不给推断 / 不给默认值，强迫用户做完所有选择

---

## 与其他角色的衔接

| 下一步 | 谁接手 | 用到本阶段的什么 |
|--------|--------|------------------|
| Step 2 | Strategist + Researcher | 整份 `project_brief.md`，重点用 Use Case / Audience / Source Materials |
| Step 3 | Strategist | Use Case 决定叙事弧选型；Page Count 决定大纲长度 |
| Step 6 | Designer | Style Preference → style_name 直接写入 `style_lock.json` |
| Step 7 | Renderer | Output Mode 决定走 7A 还是 7B（或并行） |

---

**关联文档**：
- [`00-product-principles.md`](00-product-principles.md)
- [`02-context-pack.md`](02-context-pack.md) — 下一步
- [`15-export-contract.md`](15-export-contract.md) — 项目目录约定
