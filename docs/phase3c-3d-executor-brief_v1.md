# Phase 3c / 3d 执行 Brief（给 CC）

| 字段 | 值 |
|------|-----|
| 版本 | v1.0 |
| 读者 | Phase 3 执行者（CC）、产品验收者 |
| 前置 | **3a** `9b99c29`、**3b** `59f3cf0` 已提交 |
| 母文档 | [`phase3-implementation-brief_v1.md`](phase3-implementation-brief_v1.md) |
| 工作目录 | `skills/ai-slide-producer/`（Git 根为 `skills/`） |

---

## 0. 一句话

- **3c**：让 `build_html.py` 把多 layout 内容映射做完整，并落地 **Mixed**（HTML 真引用 `images/slide-NN.png`）的可验收样例。
- **3d**：补齐 **Style Guard** + **Producer** 两篇 reference，让 Step 8–9 有章可循，Agent 不再自由发挥 `qa_report.md`。

**建议分两刀 commit**：`feat(phase3c): …` → `feat(phase3d): …`（与 3a/3b 一致）。

---

# Phase 3c — build_html 深化 + Mixed 引图

## 1. 目标与验收（Done 的定义）

| # | 验收项 | 如何证明 |
|---|--------|----------|
| C1 | `timeline` / `framework` / `two-column` 在 gallery 中 body 项按约定完整渲染 | 打开 `teaching-clean-layout-gallery/index.html` 目视 + 无 `{{` |
| C2 | `image_block` 在文件存在时输出 `<img src="images/slide-NN.png">` | Mixed 样例 P01/P07（或你选的页）浏览器可见图 |
| C3 | 文件不存在时优雅降级（占位文案或空块），**不** 404 破版 | 删掉一张图后 `build_html` 仍 `validate_html` 通过 |
| C4 | 新增 **`editorial-magazine-mixed-demo`**（或等价命名） | 见 §3.4 |
| C5 | `08-web-renderer.md`、`15-export-contract.md` 与实现一致 | 文档 diff 可读 |
| C6 | 回归命令全绿 | §6 命令块 |

**3c 明确不做**（留给 3e/3f/backlog）：

- 其余 5 套 preset CSS
- `10-style-guard.md` / `11-producer.md`（3d）
- laogouapi 异步 Jobs
- `merge-to-pptx.ts`
- 新脚本 `validate_style_guard.py`（可选，非必须）

---

## 2. 现状基线（执行前必读）

### 2.1 `build_html.py` 已有能力

```text
body → list_items()      → <ul>           （two-column 右栏、image-text 等）
body → tiles()           → framework tiles （最多 6 项，支持 "标题:正文" / "标题：正文"）
body → steps()           → timeline steps  （最多 6 项，无冒号时自动 Step N）
body → comparison_panels() → 最多 4 panel   （3a 已修）
image_block()            → 有图 <img>，无图 <span> 占位
```

`style_lock.style_name` → `assets/styles/<name>.css`（3b 已验证）。

### 2.2 已知缺口（3c 要补）

| layout | snippet 占位符 | 当前行为 | 3c 期望 |
|--------|----------------|----------|---------|
| `two-column` | 左栏用 `headline`+`key_message`，右栏 `body_items` | 右栏可多条；左栏不消费 `body[0]`/`body[1]` | **方案 A（推荐）**：`body[0]`→左栏副标题，`body[1..]`→右栏列表；不足 2 条时保持现逻辑 |
| `timeline` | `{{steps}}` | 无 `Title:描述` 时显示 Step 1/2/3 | 文档约定 Writer 写 `阶段:说明`；代码已支持，gallery 加 1 条带冒号回归即可 |
| `framework` | `{{tiles}}` | 同 tiles | gallery P06 已有 tiles；确认 4–6 tile 不截断 |
| `image-text` | `{{image_block}}` | 依赖磁盘文件 | Mixed 样例必须有真实 png |
| `comparison` | `{{comparison_panels}}` | ✅ 4 panel | 仅回归，无需再改除非发现 bug |

### 2.3 Mixed 契约（PRD + 15 已有，3c 要「样例落地」）

路径约定（相对项目根）：

```text
images/slide-01.png   # 与页序 index 对齐（1-based），零填充 2 位
```

解析顺序（`build_html.py` / `08` 须一致）：

1. `page.image_requirement.generated_image_path`（非空且文件存在）
2. 否则 `images/slide-{index:02d}.png`（及 `.jpg` / `.jpeg` / `.webp` 若你扩展探测）
3. 否则占位（**禁止**外链 URL）

**Mixed 推荐流水线**（训练营 HTML-first + 局部出图）：

```text
export_images_manifest → generate_images（仅 needed 页）→ build_html → validate_html
```

`build_html` 必须在 `generate_images` **之后**跑，Mixed 样例才看得到 `<img>`。

---

## 3. 3c 任务清单（按顺序）

### 3.1 审计并修补 `build_html.py`

1. 读 `assets/templates/layouts/*.html.snippet`，列出每个 layout 用到的 `{{...}}` 与 `page_values()` 映射表（可写在 `08-web-renderer.md` 附录）。
2. 实现 **two-column** 分列规则（§2.2 方案 A）；改后跑 gallery rebuild。
3. 确认 `tiles` / `steps` 上限与 PRD 密度一致（6 项）；超出时在 `08` 注明「Writer 不应超过 6 条」。
4. **`image_block` 增强（小）**：
   - 若 `image_requirement.needed === true` 且文件缺失，占位文案用 `visual_direction` 或固定 `Image pending (slide-NN)`，便于 Style Guard（3d）识别。
   - 保持路径白名单正则，禁止 `http://`。
5. **不要**在 `build_html.py` 里写 preset 专用 CSS。

### 3.2 更新 references

| 文件 | 更新内容 |
|------|----------|
| `references/08-web-renderer.md` | Mixed 规则、layout→占位符表、two-column body 约定、`image_block` 行为、7B 与 7A-G 顺序 |
| `references/15-export-contract.md` | Mixed 树验收步骤；`build_html` 伪代码与实现对齐 |
| `references/05-writer.md`（可选一小节） | `image_requirement.needed` 何时 true；`body` 行格式 `标题:正文` |

### 3.3 新增 Mixed 样例 `assets/examples/editorial-magazine-mixed-demo/`

**推荐做法**（避免依赖用户 API key 才能验收）：

1. 复制 `editorial-magazine-demo/source/*` 为起点，`style_lock` 保持 `editorial-magazine`。
2. `context_pack.md` 中 `Output Mode: mixed`。
3. 选 **2–3 页** 设 `image_requirement.needed: true`（建议：`cover` P01、`quote` P07、`image-text` 若 deck 含该 layout）。
4. 在 `images/` 下提交 **小体积占位 PNG**（可用 16:9 纯色块脚本生成，或从现有 `teaching-clean-demo/images/` 复制并重命名为 `slide-01.png` 等——**不要**提交大体积真图批量）。
5. `slide_plan` 对应页写 `generated_image_path: "images/slide-01.png"`（与文件一致）。
6. 跑通：

```bash
python3 scripts/build_html.py assets/examples/editorial-magazine-mixed-demo
python3 scripts/validate_html.py assets/examples/editorial-magazine-mixed-demo/index.html
```

7. 浏览器打开：指定页必须是 **`<img src="images/slide-..">`**，不是纯 `<span>`。

**可选（P1，不挡 3c）**：`swiss-system-demo` 3–4 页，或 gallery 复制一份 `style_name: swiss-system` 仅改 `style_lock` 后 rebuild（证明第二套高视觉 CSS）。

### 3.4 回归

| 样例 | 命令 |
|------|------|
| teaching-clean-layout-gallery | `build_html` + `validate_html`（工程回归） |
| editorial-magazine-demo | 同上（3b 不回归） |
| editorial-magazine-mixed-demo | 同上 + **目视 Mixed** |

更新 `assets/examples/README.md`：增加 mixed-demo 行与命令块。

### 3.5 更新 `SKILL.md` / `README.md`（仅 3c 相关）

- `SKILL.md` **当前阶段** → Phase 3c 完成 / 下一阶段 3d。
- Step 7B 可加一句：Mixed 项目在 7A-G 之后执行 `build_html.py`。
- `README.md` 阶段表增加 3c 一行。

---

## 4. 3c 验收命令（复制执行）

```bash
cd skills/ai-slide-producer

# 工程回归
python3 scripts/build_html.py assets/examples/teaching-clean-layout-gallery
python3 scripts/validate_html.py assets/examples/teaching-clean-layout-gallery/index.html

# 3b 回归
python3 scripts/build_html.py assets/examples/editorial-magazine-demo
python3 scripts/validate_html.py assets/examples/editorial-magazine-demo/index.html

# 3c 新增
python3 scripts/validate_slide_plan.py assets/examples/editorial-magazine-mixed-demo/source/slide_plan.json
python3 scripts/validate_context_lock.py assets/examples/editorial-magazine-mixed-demo/source/style_lock.json
python3 scripts/build_html.py assets/examples/editorial-magazine-mixed-demo
python3 scripts/validate_html.py assets/examples/editorial-magazine-mixed-demo/index.html

python3 -m py_compile scripts/build_html.py
```

**浏览器**：Mixed 样例中至少 2 页可见嵌入图；gallery P04 two-column、P06 framework、P07 timeline 内容无「明显少渲染」。

---

# Phase 3d — Style Guard + Producer（Step 8–9 收口）

## 1. 目标与验收（Done 的定义）

| # | 验收项 | 如何证明 |
|---|--------|----------|
| D1 | `references/10-style-guard.md` 存在且可执行 | Step 8 链接有效；含检查表 + 返工决策 |
| D2 | `references/11-producer.md` 存在且可执行 | Step 9 链接有效；含 Output Mode / 交付树 / README 模板 |
| D3 | `SKILL.md` Step 8–9 指向 10/11，目录树 10/11 标 ✅ Phase 3d | grep 无「待写 Phase 3」于 10/11 |
| D4 | `14-quality-checklist.md` 与 10/11 分工清晰 | 不重复造轮子；14 保留总表，10 管视觉，11 管交付 |
| D5 | Agent 可按文档填 `qa_report.md` | 模板字段固定，禁止自由发挥 |

**3d 明确不做**：

- 新 backend / probe 逻辑（已实施，**引用**即可）
- 7 套 preset 补齐（3e）
- UAT 全文扩写（3f，可在 3d 末尾加 5 条勾选占位）

---

## 2. `10-style-guard.md` 必写章节

建议结构（可直接作目录）：

1. **角色**：Step 8 视觉守门；对照 `style_lock.json` + preset（`12-style-presets.md`）。
2. **输入**：`style_lock.json`、`index.html`、`images/`、`images_manifest.json`（若有）、`style_name` 对应 CSS。
3. **与 Reviewer / Producer 边界**（摘 PRD §8.8）：
   - Reviewer：内容、事实、叙事（Step 5 + Step 8 复检）
   - Style Guard：颜色、字体、密度、layout 漂移、图缺失、占位符残留
   - Producer：目录、README、可见性（Gate 6）
4. **检查表**（表格，每项 pass / warn / fail）：

| 检查项 | 标准 |
|--------|------|
| CSS 变量 | `--asp-bg` 等与 `style_lock` 一致（目视或解析 `index.html` 内 `:root`） |
| Preset 漂移 | 未出现 teaching-clean 灰卡片感却选了 editorial 等（主观 + forbidden[]） |
| 占位符 | 无 `{{...}}` |
| 图片契约 | `needed=true` 的页在 Mixed 下有文件或 manifest `ok`；否则 warn |
| 文本密度 | 对照 `style_lock.density` 与 `14` 密度表 |
| layout 完整 | section 数 = total_pages；`data-layout` 与 plan 一致 |
| 溢出风险 | 单页 body > 6 或标题过长 → warn |

5. **返工决策**：
   - visual fail → `regenerate_slide.py` 或重写 `style_lock` + 重跑 `build_html`
   - 仅 manifest pending → 记入 qa warn，不阻塞 html-only 交付
6. **输出**：写入 `qa_report.md` 的 **Style Guard** 小节（模板见下）。

---

## 3. `11-producer.md` 必写章节

1. **角色**：Step 9 交付组装；满足 Gate 6 Result Visible。
2. **Output Mode 决策树**（文字 + mermaid 可选）：
   - Step 1：优先 `probe_image_backend.py <project>`（见 [`plan-agent-backend-probe_v1.md`](plan-agent-backend-probe_v1.md)）
   - 用户 override > probe > 场景默认（训练营：**mixed**；纯阅读：**html-only**；只要图：**image-first**）
   - backend 不可用 → `html-takeover` / `prompts-only`，须在 README 说明
3. **三种交付树**：引用 `15-export-contract.md`，各树 **必含文件清单** + 缺文件时如何处理。
4. **项目 README 模板**（Markdown 代码块）：怎么打开 `index.html`、怎么改 `slide_plan`、怎么 `regenerate_slide`、`images/` 含义。
5. **Gate 6 检查**：用户至少能打开 HTML 或看到 `images/slide-*.png` 目录。
6. **与脚本的关系**（表）：

| 步骤 | 脚本 |
|------|------|
| 7A-P | `export_images_manifest.py` |
| 7A-G | `generate_images.py` |
| 7B | `build_html.py` |
| 局部重生 | `regenerate_slide.py` |
| 探测 | `probe_image_backend.py` |

7. **禁止**：Agent 手写 `index.html`；交付根目录混乱命名。

---

## 4. 联动修改（3d 一并做）

| 文件 | 动作 |
|------|------|
| `SKILL.md` | Step 8→`10-style-guard`；Step 9→`11-producer`；信息架构 10/11 ✅；更新「当前阶段」 |
| `references/14-quality-checklist.md` | 文首增加「详见 10/11」；`qa_report.md` 拆为三小节模板 |
| `README.md` | 快速入口增加 10、11；阶段表 3d 完成 |
| `docs/README.md` | 索引本文档 |

### `qa_report.md` 统一模板（写入 14 或 11）

```markdown
# QA Report

**Status**: pass | pass-with-warnings | fail
**Output Mode**: <from context_pack>
**Checked**: YYYY-MM-DD

## Content (Reviewer)
- …

## Visual (Style Guard)
- …

## Delivery (Producer)
- …

## Follow-ups
- …
```

---

## 5. 3d 验收（文档 + 轻量运行）

```bash
# 无新脚本时：确认链接与样例仍可构建
python3 scripts/build_html.py assets/examples/editorial-magazine-mixed-demo
python3 scripts/validate_html.py assets/examples/editorial-magazine-mixed-demo/index.html
```

**人工**：用 10 的检查表扫一遍 mixed-demo 的 `index.html` + `style_lock.json`，在 `qa_report.md` 填一例（可放在 mixed-demo 的 `source/` 或项目根，与 15 一致即可）。

---

## 6. 提交与范围纪律

### 建议 commit

```text
feat(phase3c): mixed demo and build_html layout mapping

feat(phase3d): style guard and producer references
```

### 不要提交

- `ai-slide-producer.zip`
- `teaching-clean-demo/images/`（本地出图）
- 用户 `.env`

---

## 7. 产品方预置决策（执行中勿改，除非 Peng 另说）

| 决策 | 值 |
|------|-----|
| Mixed 样例 preset | `editorial-magazine` |
| 占位图策略 | 仓库内小 PNG，不绑 API |
| 训练营默认 Output Mode | `mixed`（HTML-first + 封面/金句图） |
| 3c 后是否必须 swiss demo | 否（P1） |

---

## 8. 完成后母 brief 勾选建议

在 [`phase3-implementation-brief_v1.md`](phase3-implementation-brief_v1.md) §4 表旁可加状态列，或由 PM 在 3f 统一勾选：

- [x] 3a / 3b
- [ ] 3c — Mixed + build_html
- [ ] 3d — 10 / 11
- [ ] 3e — 7 preset 齐
- [ ] 3f — UAT E2E

---

**关联**：[`skill-uat-checklist_v1.md`](skill-uat-checklist_v1.md) · [`phase2-implementation-brief_v1.md`](phase2-implementation-brief_v1.md) · [`plan-agent-backend-probe_v1.md`](plan-agent-backend-probe_v1.md)
