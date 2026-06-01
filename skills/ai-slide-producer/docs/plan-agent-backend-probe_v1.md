# 待核对计划｜Agent 图片 Backend 探测与 `.env` 脱节

| 字段 | 值 |
|------|-----|
| 文档版本 | v1.1 |
| 状态 | **已实施** |
| 读者 | 产品方、执行者、熟悉 Cursor/CraftAgents 协作者 |
| 关联 | [`SKILL.md`](../SKILL.md) §Output Mode 探测、[`01-intake-brief.md`](../references/01-intake-brief.md)、[`02-context-pack.md`](../references/02-context-pack.md)、[`scripts/generate_images.py`](../scripts/generate_images.py)、[`scripts/probe_image_backend.py`](../scripts/probe_image_backend.py) |

---

## 1. 问题陈述（现象）

用户在 Cursor 中加载 **ai-slide-producer** Skill，用 Agent（如 DeepSeek v4）走 Step 1 Intake 时，Round 1 确认里出现：

```text
图片 Backend  ❌ 不可用（无 API Key）
→ Output Mode 可能被判为 html-takeover
```

与此同时，在同一台机器、同一 Skill 目录下：

- 已配置 `skills/ai-slide-producer/.env`（`OPENAI_API_KEY`、`OPENAI_BASE_URL=https://laogouapi.com/v1`、`gpt-image-2`）
- 本机执行 `python3 scripts/generate_images.py … --only P01` **可以成功出图**（`images/slide-01.png`，manifest `ok`）

即：**脚本路径可用，Agent 对话路径误判为无 Key。**

---

## 2. 根因分析（待核对是否同意）

### 2.1 不是「脚本读不了 `.env`」

`generate_images.py` 在运行时通过 `load_env()` 按顺序读取（**只读第一个存在的文件，不合并**）：

1. 当前工作目录 `./.env`
2. `<project-dir>/.env`
3. `<skill-root>/.env`（即 `skills/ai-slide-producer/.env`）

已实测：在 `ai-slide-producer/` 下跑脚本可加载 Key 并调用 laogouapi 同步 API `POST /v1/images/generations`。

**结论（待核对）**：Phase 2b 脚本与 `.env` 机制正常；问题不在 `load_env` 实现。

### 2.2 是「Agent Step 1 探测」与「脚本执行」两套上下文

| 维度 | Agent Step 1（Intake） | 本机脚本（7A-G） |
|------|------------------------|------------------|
| 执行者 | LLM 按 SKILL 文字推理 | Python 进程 |
| 当前契约要求 | 查 runtime 原生 image 工具；否则查 **环境变量** `OPENAI_API_KEY` 等 | 跑脚本时 `load_env` + `os.environ` |
| Cursor 实际情况 | Agent **通常看不到** 用户磁盘上的 `.env`（gitignore、安全策略）；也**不会自动**继承用户终端里 `source .env` 的结果 | 用户在正确 cwd 下执行即可 |
| 结果 | 易判 **backend unavailable** → `html-takeover` | 可 **image-first** 真出图 |

**结论（待核对）**：误判来自 **Output Mode 探测发生在 Agent 认知层**，且未强制跑任何「只读探测脚本」。

### 2.3 与 `.env.example` 文档的小偏差

`.env.example` 头部写的是查找顺序含 `~/.ai-slide-producer/.env`，但 **`generate_images.py` 的 `load_env()` 并未实现第 3 路径（用户主目录）**。  
这不导致 Agent 误判，但可能造成「我写在 ~/.ai-slide-producer/.env 为什么无效」的困惑。

**待核对项**：是否统一文档 vs 补实现 `~/.ai-slide-producer/.env`。

### 2.4 网关 Cloudflare（已处理，附录）

laogouapi 对 Python 默认 `urllib` User-Agent 曾返回 `403 / error 1010`；`curl` 正常。  
已在 `generate_images.py` 增加 `User-Agent` 请求头（commit `8bdfdc5` 一带）。  
**与 Agent 误判无 Key 无关**，但属同一网关环境下的实测记录。

---

## 3. 上游参考：baoyu-slide-deck 的做法

路径：`references/baoyu-skills/skills/baoyu-slide-deck/SKILL.md` §Image Generation Tools。

| 要点 | baoyu | ai-slide-producer（现状） |
|------|-------|---------------------------|
| 探测优先级 | ① 用户当次指定 ② `EXTEND.md` 偏好 ③ **Runtime 原生工具**（`imagegen` 等）④ 已安装的 **子 Skill**（`baoyu-imagine`） | ① 原生工具 ② **环境变量**（Agent 猜） |
| 密钥存放 | 跑 `bun scripts/main.ts` 时用 `process.env`；偏好写在 **EXTEND.md**（无 Key） | Key 在 **`.env`**，偏好未单独 EXTEND |
| Agent 是否读 `.env` | **不依赖** Agent 读 `.env`；依赖「能否调用工具/Skill/脚本」 | 契约写「查 env」，Agent 常查不到 |
| 无 backend 时 | 明确告知用户并询问如何继续 | 自动 `html-takeover` + 保留 Prompts |

**可借鉴（待核对）**：

- 把「backend 是否可用」变成 **可执行探测**（跑脚本 / 调 Skill），而不是让 LLM 假设环境变量。
- 区分 **配置声明**（用哪个 backend）与 **密钥**（仍在 `.env`，不进对话）。

---

## 4. 目标（若计划批准）

1. Step 1 Round 1 的 **Backend / Output Mode** 与用户在终端跑 `generate_images.py` 的结论 **一致**。
2. **不把 API Key 打进对话、不写进 `project_brief.md` 明文**。
3. 保持现有 Phase 2 脚本行为；改动尽量小、可回归。
4. UAT 勾选表（[`skill-uat-checklist_v1.md`](skill-uat-checklist_v1.md)）可增加一条「Agent 探测与脚本一致」。

---

## 5. 方案选项（请核对择一或组合）

### 方案 A — 仅文档 + 用户口令（零代码）

**做法**：

- 在 `SKILL.md` / `01-intake-brief` / UAT 中写明：Cursor Agent **不能**假定可见 `OPENAI_API_KEY`；用户若已配 `.env`，须在对话中说明「backend 已在本机 skill 目录配置，请记 available」；Step 7 由用户或 Agent 触发终端跑 `generate_images.py`。
- 修正 `.env.example` 与 `load_env` 路径说明一致。

**优点**：无开发量，立即可用。  
**缺点**：每次依赖用户记忆；Agent 仍可能忽略口令。

**适合**：短期 UAT、单人使用。

---

### 方案 B — 增加 `probe_image_backend.py`（推荐，待核对）

**做法**：

1. 新增 `scripts/probe_image_backend.py`：
   - 复用 `generate_images.load_env(skill_root, project_dir)`；
   - 检查 `OPENAI_API_KEY` / `GEMINI_API_KEY` 是否非空（及可选 `IMAGE_BACKEND`）；
   - **stdout 只输出 JSON**，例如：  
     `{"openai":{"available":true},"gemini":{"available":false},"recommended":"openai"}`  
     **禁止打印 Key 值**。
2. 修改 `SKILL.md` Step 1：**在 Output Mode 探测前必须**在 `<skill-root>` 执行：  
   `python3 scripts/probe_image_backend.py`  
   并以脚本输出为准写入 `project_brief.md` § Backend probe。
3. Agent 用 **终端工具**跑上述命令（Cursor 可做到），不读 `.env` 文件内容。

**优点**：与 baoyu「可执行探测」对齐；行为可回归、可写进 CI（无 Key 时 `available:false`）。  
**缺点**：依赖 Agent 愿意/能够跑终端；多一个脚本维护点。

**待核对**：

- exit code：无 Key 时 `0` 但 `available:false`，还是 `1`？
- 是否探测「连通性」（打一次 dry-run API）还是只探测「Key 是否存在」？（建议 v1 只探测 Key 存在，避免 UAT 耗额度）

---

### 方案 C — `source/.env.backend` 或 EXTEND 声明（半结构化）

**做法**：

- 允许在项目 `source/env.backend.json`（或 skill 级 `EXTEND.md`）写：  
  `{ "image_backend": "openai", "configured": true }` **不含 Key**；
- Agent 读该 JSON 判断 available；Key 仍仅 `.env` 供脚本使用；
- 用户提供 Key 后，由脚本或一次性命令生成/更新该声明文件。

**优点**：Agent 可读、无密钥；接近 baoyu EXTEND。  
**缺点**：双份配置易漂移（声明有、`.env` 无 Key）；需约定谁维护。

---

### 方案 D — Cursor 规则 / MCP 注入环境变量

**做法**：

- 在 Cursor Project Rules 或用户级规则写：本仓库已配置 image backend，Intake 时视为 available；
- 或通过 MCP/Secrets 把 `OPENAI_API_KEY` 注入 Agent 运行环境（若平台支持）。

**优点**：Agent 侧「env 可见」与脚本一致。  
**缺点**：绑定 Cursor/平台；密钥进 Agent 运行时，安全与审计要单独评估；不可移植到其他 Agent。

---

## 6. 建议决策矩阵（起草，供核对修改）

| 若优先考虑… | 建议 |
|-------------|------|
| 最快能测、少改代码 | **A**，UAT 加用户口令 |
| 长期正确、可移植 | **B**（主） + **A**（兜底说明） |
| 与 baoyu 体验一致 | **B + C**（EXTEND 只声明 backend 类型） |
| 仅 Cursor、不在乎移植 | **D** 可作为个人配置，不进 Skill 主契约 |

**起草推荐（待你方拍板）**：**B + A** — 实现 probe 脚本 + 文档保留人工 override。

---

## 7. 实施清单（批准后再做）

- [x] 核对 §2 根因是否同意
- [x] 在 §5 选定方案（A/B/C/D 或组合）
- [x] 若选 B：实现 `probe_image_backend.py` + 单测/文档示例输出
- [x] 更新 `SKILL.md`、`01-intake-brief.md`、`02-context-pack.md` 探测流程
- [x] 统一 `.env.example` 与 `load_env` 路径（是否加 `~/.ai-slide-producer/.env`）
- [x] 更新 `skill-uat-checklist_v1.md` §0 / §B（Agent 探测与 probe 一致）
- [x] 可选：README 增加「Agent 误报无 Key」故障排查一节

**不在本计划内**：

- laogouapi 异步 Jobs（`POST /images/jobs/...`）接入 `generate_images.py`
- Phase 3 叙事 references 全套

---

## 8. 验收标准（实施后）

| # | 标准 |
|---|------|
| 1 | 用户仅在 `skill-root/.env` 配置 Key、**不在对话中贴 Key** |
| 2 | Agent 在 Step 1 执行 probe 后，Round 1 显示 `backend: available (openai)`（或等价文案） |
| 3 | 同一环境下 `generate_images.py --only P01` 仍为 `ok` |
| 4 | 删除/清空 `.env` 中 Key 后，probe 输出 `available:false`，Output Mode 为 `html-takeover` 且 **明示**用户 |
| 5 | `project_brief.md` 中 **不出现** 完整 API Key |

---

## 9. 开放问题（核对结论）

| ID | 问题 | 核对结论 |
|----|------|----------|
| Q1 | 根因 §2 是否同意？ | **同意**。Agent 对话环境/沙箱与终端运行环境不同，CraftAgents 在 MCP/子进程中也会过滤敏感环境变量。 |
| Q2 | 选定方案：A / B / C / D / 组合？ | **B + A 组合**。实现轻量 JSON 探测脚本 `probe_image_backend.py`，并保留用户手动口令 Override 兜底。 |
| Q3 | probe 是否只做「Key 存在」还是必须 API 连通性探测？ | **静态存在性检测为主**。但探测脚本支持可选参数 `--test-connection`，供按需排查连通性。 |
| Q4 | 是否实现 `~/.ai-slide-producer/.env` 加载？ | **是**。已在 `load_env` 中添加 `~/.ai-slide-producer/.env` 支持。 |
| Q5 | Agent 误报时，是否允许用户一句话覆盖（不跑 probe）？ | **是**。`SKILL.md` 中将用户手动指定设为最高优先级。 |
| Q6 | 核对人与日期 | peng / 2026-05-21 |

---

## 10. 修订记录

| 版本 | 日期 | 说明 |
|------|------|------|
| v1 | 2026-05-21 | 初稿：问题 + baoyu 对照 + 方案 A–D + 待核对 |
