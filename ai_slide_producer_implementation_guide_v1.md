# AI Slide Producer｜参考实施指导 v1.0

> **文档性质**：`ai_slide_producer_prd_v1.md` 的补充文档，不是 PRD 替代品。  
> **用途**：从 PRD 目标倒推「要建什么、从哪抄什么、抄到哪」，供实现 `ai-slide-producer` Skill 时对照。  
> **参考样本**：本仓库 `references/` 下已克隆的三个项目（2026-05 快照）。

| 样本 | 路径 | 上游仓库 |
|------|------|----------|
| ppt-master | `references/ppt-master/` | https://github.com/hugohe3/ppt-master |
| guizang-ppt-skill | `references/guizang-ppt-skill/` | https://github.com/op7418/guizang-ppt-skill |
| baoyu-slide-deck | `references/baoyu-skills/skills/baoyu-slide-deck/` | https://github.com/JimLiu/baoyu-skills |

**阅读顺序建议**：先读 PRD §6–§9、§12–§14 → 本文 §2 总映射表 → 按你正在实现的模块跳读 §3–§5 → 按 §6 排期落地。

---

## 1. 三个样本与 PRD 的分工

PRD 附录 A 已做原则提炼；本文补齐**可落地的文件级索引**。

| PRD 能力域 | 主借鉴样本 | 次要借鉴 | PRD 章节 |
|------------|------------|----------|----------|
| 开工前需求澄清 | guizang | baoyu `confirmation.md` | §9 Step 1、Gate 1 |
| 叙事弧 / 大纲 | guizang、baoyu | ppt-master Strategist | §9 Step 3 |
| 逐页计划 schema | baoyu `outline-template.md` | PRD §9 Step 4 字段 | §9 Step 4 |
| 内容审核 Reviewer | ppt-master `strategist.md` 大纲部分 | baoyu Step 4 | §9 Step 5 |
| Design Spec + Style Lock | ppt-master | baoyu dimensions | §9 Step 6、§12 |
| **HTML / Web Slides** | **guizang** | PRD §10 | §5.2.2、§9 Step 7B |
| **Image Slides + Prompt 资产** | **baoyu-slide-deck** | ppt-master `image_gen.py` | §5.2.1、§9 Step 7A |
| 图片生成 CLI / 多 backend | ppt-master | baoyu `baoyu-image-gen` | §5.2.1、§11 |
| Gate / 串行管线 / 禁止跨阶段 | ppt-master `SKILL.md` 顶部规则 | — | §6.2、§13 |
| Context Lock 每页重读 | ppt-master `spec_lock.md` | PRD `style_lock.json` | §12 |
| 中间态 outline/prompts/images-only | baoyu-slide-deck | PRD §9 Step 7C | §6.6、§15 路径 D |
| 质量检查 | guizang `checklist.md` | ppt-master `svg_quality_checker.py` | §9 Step 8 |
| 交付目录结构 | PRD §9 Step 9 | baoyu File Layout | §9 Step 9 |
| PPTX 导出（v1 可选） | baoyu `merge-to-pptx.ts` | ppt-master `svg_to_pptx.py` | PRD v1 未强制 |

**刻意不照搬（PRD 已排除或路线不同）**：

- ppt-master 主产物是 **SVG → PPTX**，不是 PRD 的 HTML/Image 双轨（见 `references/ppt-master/skills/ppt-master/SKILL.md` Step 6–7）。
- ppt-master Step 1 的 PDF/DOCX/PPTX 解析（`scripts/source_to_md/`）— PRD §5.1 写明 v1 不做，可外置。
- ppt-master Live Preview（`workflows/live-preview.md`、`scripts/svg_editor/server.py`）— PRD v1 未要求。
- guizang 仅 2 套视觉 → PRD 要 7 套 preset，需扩展而非复制。

---

## 2. PRD 九步主流程 → 参考对照总表

| PRD Step | 名称 | guizang | ppt-master | baoyu-slide-deck |
|----------|------|---------|------------|------------------|
| 1 | Intake / 需求澄清 | `SKILL.md` §Step 1（7 问） | Step 4 Eight Confirmations 子集 | `SKILL.md` Step 2 + `references/confirmation.md` |
| 2 | Context Pack | 叙事弧 + 项目记录 | `design_spec.md` 前半 | `analysis.md` 模式（Step 1.2） |
| 3 | Outline | Hook→Takeaway | Strategist 内容大纲 | `outline.md` + `references/outline-template.md` |
| 4 | Slide Plan | `layouts.md` 页角色 | spec_lock `page_*` 字段 | outline 每页 Type/Layout |
| 5 | Narrative Review | `checklist.md` 内容项 | Reviewer 逻辑（分散在 strategist） | Step 4 Review Outline |
| 6 | Design Spec | `themes.md` / `themes-swiss.md` | `design_spec.md` + `spec_lock.md` | `references/styles/*.md` + dimensions |
| 7A | Image Render | `image-prompts.md`（配图） | Step 5 + `image_gen.py` | Step 5–7 全流程 |
| 7B | Web Render | Step 2–3 模板填充 | （无，走 SVG） | （无，走 raster） |
| 7C | 中间态 | — | split mode / resume | `--outline-only` 等 |
| 8 | Quality Check | `checklist.md` + `validate-swiss-deck.mjs` | `svg_quality_checker.py` | 人工 review 步骤 |
| 9 | Delivery | `index.html` + `images/` | `exports/*.pptx` | `slide-deck/{slug}/` |

---

## 3. guizang-ppt-skill（HTML 主线）

### 3.1 全流程（6 步）

| 步骤 | 做什么 | 必读文件 |
|------|--------|----------|
| Step 1 | 需求澄清（风格 A/B、受众、时长、素材、主题色、硬约束）；可选叙事弧 | `references/guizang-ppt-skill/SKILL.md` L48–L151 |
| Step 2 | 拷贝模板、改 `<title>`、选主题色替换 `:root` | `SKILL.md` L153–L203；模板 `assets/template.html` 或 `assets/template-swiss.html` |
| Step 3 | Pre-flight 类名、主题节奏、选 layout 粘贴、图片比例 | `references/layouts.md` 或 `layouts-swiss.md` + `swiss-layout-lock.md` |
| Step 4 | checklist 自检 + 浏览器视觉核对 | `references/checklist.md`；B 风跑 `scripts/validate-swiss-deck.mjs` |
| Step 5 | `open index.html` 本地预览 | `SKILL.md` L442–L450 |
| Step 6 | 按反馈改 inline style | `SKILL.md` L452–L455 |

**加载顺序（官方）**：`SKILL.md` → 主题 `themes*.md` → 模板 `<style>` → layouts →（B）`swiss-map-component.md` → 配图 `image-prompts.md` → `checklist.md`  
见 `SKILL.md` L483–L497。

### 3.2 可借鉴资产（复制/改写到本项目的 `assets/`）

| 类型 | 参考路径 | 建议映射到 PRD |
|------|----------|------------------|
| HTML 种子（杂志风） | `references/guizang-ppt-skill/assets/template.html` | `assets/templates/web-slide-template.html` 或 `editorial-magazine` 变体 |
| HTML 种子（瑞士风） | `assets/template-swiss.html` | `assets/templates/` 中 `swiss-system` 变体 |
| 翻页/键盘/ESC 索引 JS | 两模板内嵌 `<script>`（底部 module） | PRD §10.2 交互 |
| Motion 离线兜底 | `assets/motion.min.js` | 可选依赖，CDN 失败时降级 |
| 截图背景资产 | `assets/screenshot-backgrounds/` | Mixed/教学类截图页；对应 PRD Image+HTML |
| 风格 A 主题色 5 套 | `references/themes.md` 内 `:root` 块 | → `style-presets/editorial-magazine.json` + CSS |
| 风格 B 主题色 4 套 | `references/themes-swiss.md` | → `style-presets/swiss-system.json` |
| 布局骨架 ×10（A） | `references/layouts.md` 各 `<section>` 块 | PRD §10.3 页面类型 → `layout_type` 映射 |
| 布局骨架 ×22（B） | `references/layouts-swiss.md` + `swiss-layout-lock.md` | 同上，瑞士网格页 |
| 地图组件（B S08） | `references/swiss-map-component.md` | PRD Framework/Timeline 扩展 |
| 组件样式手册 | `references/components.md` | Designer / Web Renderer 规范 |
| 配图 prompt 类型 | `references/image-prompts.md` | → `assets/templates/image-prompt-template.md` |
| 截图 framing | `references/screenshot-framing.md` | Image 路径辅助规则 |
| QA 清单 | `references/checklist.md` | → `references/14-quality-checklist.md` |

### 3.3 可借鉴代码/脚本

| 文件 | 作用 | 本项目用法 |
|------|------|------------|
| `scripts/validate-swiss-deck.mjs` | 校验 `data-layout`、图片槽位、禁止 SVG 内文字等 | 移植或改写为 `scripts/validate_html.py`（Web QA） |
| 模板内 WebGL shader | `template.html` / `template-swiss.html` 内 canvas | PRD `teaching-clean` 可简化去掉 WebGL，保留翻页内核 |

### 3.4 与 PRD 的直接映射

| PRD 要求 | guizang 现成实现位置 |
|----------|---------------------|
| 单页 HTML、16:9、横向翻页 | 模板 `section.slide` + 翻页 JS |
| 键盘 ←→、指示器、移动端滑动 | 模板 JS（见 template 底部） |
| ESC 缩略图索引 | 瑞士模板 checklist L431 |
| 10 种页面类型 | layouts 1–10（A）/ S01–S22（B） |
| 开工 7 问澄清 | `SKILL.md` L61–L71 |
| Hook→Takeaway 叙事弧 | `SKILL.md` L87–L95 |
| 图片命名 `{页号}-{语义}.ext` | `SKILL.md` L105–L108 |
| 主题色锁定、禁止随意 hex | `SKILL.md` L181–L202 |
| 不依赖构建工具 | 纯静态 HTML |

### 3.5 实现时注意

- guizang **A/B 两套类名不互通**（`SKILL.md` L169–L173）→ PRD 7 preset 应各用独立 CSS 命名空间或 BEM 前缀，避免混用。
- 字体依赖 Google Fonts CDN（`template.html` L7–L9）→ PRD「本地可打开」需准备 `web-slide-template-minimal.html` 系统字体回退。
- Codex 配图流程（`SKILL.md` L128–L151）→ 对齐 PRD Image Renderer + runtime-native backend 规则。

---

## 4. ppt-master（生产纪律 + 图片 CLI + Context Lock）

### 4.1 全流程（7 步主链 + 独立 workflow）

**主入口**：`references/ppt-master/skills/ppt-master/SKILL.md`

| 步骤 | GATE / 阻塞 | 关键动作 | 关键路径 |
|------|-------------|----------|----------|
| Step 1 | 有源材料 | PDF/DOCX/URL→MD；无源则 `topic-research` | `scripts/source_to_md/*.py`；`workflows/topic-research.md` |
| Step 2 | Step 1 完成 | `project_manager.py init` + `import-sources --move` | `scripts/project_manager.py` |
| Step 3 | Step 2 完成 | 仅**显式路径**触发模板/品牌拷贝 | `templates/layouts/`、`templates/brands/`、`layouts_index.json` |
| Step 4 Strategist | Step 3 完成 | Eight Confirmations ⛔BLOCKING；输出 `design_spec.md` + `spec_lock.md` | `references/strategist.md`；`templates/design_spec_reference.md`；`templates/spec_lock_reference.md` |
| Step 5 Image | design spec 确认；有 ai/web 行 | manifest 模式 `image_gen.py` | `references/image-base.md`；`image-generator.md`；`scripts/image_gen.py` |
| Step 6 Executor | Step 4/5 完成 | 逐页 SVG；每页重读 spec_lock；质量门 | `references/executor-base.md`；`scripts/svg_quality_checker.py` |
| Step 7 Export | SVG+notes 就绪 | split notes → finalize → svg_to_pptx | `total_md_split.py`；`finalize_svg.py`；`svg_to_pptx.py` |

**管线铁律（必须写入本 Skill `SKILL.md` 顶部）**：`SKILL.md` L19–L27  
— 串行、BLOCKING 硬停、禁止跨阶段打包、每步 GATE、禁止子 agent 生成 SVG、逐页顺序生成。

**独立 Workflow 索引**：`SKILL.md` L73–L84

| Workflow | 路径 | PRD 是否采纳 |
|----------|------|--------------|
| topic-research | `workflows/topic-research.md` | 可选（外置调研） |
| create-template | `workflows/create-template.md` | Phase 2+ |
| resume-execute | `workflows/resume-execute.md` | 类似长 deck 分 session |
| live-preview | `workflows/live-preview.md` | v1 不采纳 |
| verify-charts | `workflows/verify-charts.md` | HTML 图表校准时可参考思路 |
| generate-audio | `workflows/generate-audio.md` | v1 不采纳 |

### 4.2 Context Lock（→ PRD `style_lock.json`）

| 概念 | ppt-master 位置 | 本项目落地 |
|------|-----------------|------------|
| 机器可读锁 | `<project>/spec_lock.md`（骨架 `templates/spec_lock_reference.md`） | `style_lock.json`（PRD §12 示例） |
| 人类可读说明 | `<project>/design_spec.md`（骨架 `templates/design_spec_reference.md`） | `design_spec.md` |
| 每页生成前重读 | `executor-base.md` §2.1；`SKILL.md` L375 | Web/Image Renderer 规范写入 `09-image-renderer.md`、`08-web-renderer.md` |
| 同步更新 | `scripts/update_spec.py` | v1 可手工改 lock；后续脚本化 |

**spec_lock 字段参考**：`templates/spec_lock_reference.md` — `canvas`、`colors`（含 `image_rendering`/`image_palette`）、`typography`、`icons`、`images`、`page_rhythm`、`page_layouts`、`page_charts`。

### 4.3 图片生成基础设施（PRD Step 7A 核心依赖）

| 资源 | 路径 | 说明 |
|------|------|------|
| 统一 CLI | `scripts/image_gen.py` | 多 backend；manifest 批量；`--list-backends` |
| 配置加载 | `scripts/config.py`；`.env` 搜索顺序见 `image_gen.py` L23–L28 | cwd → repo root → `~/.ppt-master/.env` |
| 文档 | `scripts/docs/image.md`；`references/image-generator.md` | PRD 写的 Gemini/OpenAI 在此有完整 env 表 |
| 图片流程总则 | `references/image-base.md` | 行状态机、失败→Needs-Manual |
| 渲染风格库 | `references/image-renderings/_index.md` + 各 `*.md` | → PRD Style Preset 的 `image_style` |
| 调色板库 | `references/image-palettes/_index.md` | → `color_palette` |
| 版图类型 | `references/image-type-templates/_index.md` | Prompt 结构参考 |
| 布局模式 | `references/image-layout-patterns.md`、`image-layout-spec.md` | 图文混排尺寸数学 |
| 网络搜图 | `scripts/image_search.py`；`references/image-searcher.md` | PRD v1 可选 |
| 水印去除 | `scripts/gemini_watermark_remover.py` | 可选 |

**manifest 工作流（ppt-master 强制）**：`SKILL.md` L316–L322  
1. 写 `images/image_prompts.json`  
2. `python3 image_gen.py --manifest ...`  
3. `image_gen.py --render-md` → `image_prompts.md`  

→ 对齐 PRD「Prompt 先落盘再生成」与 `images_manifest.json`。

**Backend 注册表**：`image_gen.py` 内 `BACKEND_REGISTRY`（gemini、openai、qwen、zhipu 等）— PRD v1 建议只封装 **gemini + openai** 两个 core tier。

### 4.4 项目结构与脚本（交付/校验借鉴）

| 脚本 | 路径 | 借鉴点 |
|------|------|--------|
| 项目初始化 | `scripts/project_manager.py` | 统一 `project-name/source/` 目录 |
| 源分析 | `scripts/analyze_images.py` | 禁止直接 read 图片文件 |
| SVG 质检 | `scripts/svg_quality_checker.py` | → `validate_slide_plan.py` / HTML 版 QA |
| 批量校验 | `scripts/batch_validate.py` | 多样本回归 |
| 错误提示 | `scripts/error_helper.py` | 用户可读失败信息 |

**项目目录惯例**（Executor 产出）：`svg_output/`、`notes/`、`images/`、`sources/`、`templates/` — 对照 PRD §9 Delivery 的 `source/`、`prompts/`、`images/`。

### 4.5 Strategist / Gate（→ PRD Gate 1–4）

| 机制 | 位置 |
|------|------|
| Eight Confirmations 模板 | `templates/design_spec_reference.md`；阻塞说明 `SKILL.md` L249–L251 |
| 画布格式 | `references/canvas-formats.md` |
| 角色切换协议 | `SKILL.md` L487–L495 |
| split mode 长任务 | `workflows/resume-execute.md`；`SKILL.md` L262–L267 |

### 4.6 与 PRD 的差异（实现时勿混淆）

- ppt-master 最终交付是 **PPTX**（`svg_to_pptx.py`），PRD 是 HTML/Image。
- 「图片」在 ppt-master 里常嵌入 SVG/PPTX；PRD Image 路径是 **独立 raster 页图**（baoyu 模型）。
- ppt-master 的 `spec_lock` 面向 SVG 坐标系；PRD `style_lock.json` 需增加 `canvas_ratio`、`density`、`forbidden`（PRD §12）等 Web/Image 字段。

---

## 5. baoyu-slide-deck（Image 主线 + 中间态 + 风格参数化）

### 5.1 全流程（9 步）

**主入口**：`references/baoyu-skills/skills/baoyu-slide-deck/SKILL.md`

| 步骤 | 门禁 | 产出 | 参考文件 |
|------|------|------|----------|
| 1 Setup | 检查已有 `slide-deck/{slug}/` | `analysis.md`、`source.md` | `references/analysis-framework.md`；`confirmation.md`（冲突处理） |
| 2 Confirmation | ⚠️ 硬门禁，默认必须确认 | 更新 `analysis.md` | `references/confirmation.md`（Round 1/2 全文） |
| 3 Outline | — | `outline.md` | `references/outline-template.md`；`references/styles/{preset}.md` |
| 4 Review Outline | 可选 | 用户改 outline | `confirmation.md` |
| 5 Prompts | 每页 prompt 文件 | `prompts/NN-slide-{slug}.md` | `references/base-prompt.md`；`references/layouts.md` |
| 6 Review Prompts | 可选 | — | `confirmation.md` |
| 7 Images | prompt 必须先存在 | `NN-slide-{slug}.png` | 顶部 `## Image Generation Tools`；`## Batch Generation Policy` |
| 8 Merge | 全部图完成 | `.pptx`、`.pdf` | `scripts/merge-to-pptx.ts`；`scripts/merge-to-pdf.ts` |
| 9 Summary | — | 用户可见摘要 | `SKILL.md` L314+ |

**CLI 中间态（对齐 PRD §9 Step 7C）**：

| 选项 | 行为 | PRD 模式 |
|------|------|----------|
| `--outline-only` | 停在 Step 3 后 | `outline-only` |
| `--prompts-only` | 停在 Step 5 后 | `prompts-only` |
| `--images-only` | 从 Step 7 开始 | `images-only` |
| `--regenerate N` | 只重生指定页 | `regenerate slide N` |

见 `SKILL.md` L100–L103、L274–L305。

### 5.2 风格系统（→ PRD 7 Style Presets）

| 机制 | 位置 | PRD 映射 |
|------|------|----------|
| 17 套 preset | `SKILL.md` L109–L130；`references/styles/*.md` | PRD 7 套需新建或从 subset 挑选映射 |
| 四维组合 texture/mood/typography/density | `references/dimensions/*.md`、`presets.md` | PRD §7.3 `style-presets/*.json` 字段 |
| 内容信号自动选风格 | `SKILL.md` L144–L166 Auto-Selection 表 | Strategist / Designer 规则 |
| 页数启发式 | `SKILL.md` L168–L175 | Intake 页数建议 |

**单 preset 规格示例路径**：

- `references/styles/blueprint.md` → PRD `blueprint`
- `references/styles/sketch-notes.md` → PRD `sketch-notes`
- `references/styles/corporate.md` → PRD `corporate`
- …（共 17 个，见 `references/styles/` 目录 listing）

### 5.3 Image 生成规则（必须写入 `09-image-renderer.md`）

| 规则 | 出处 |
|------|------|
| 禁止 SVG/HTML/Canvas 冒充 raster | `SKILL.md` L41 |
| 禁止在 bitmap 上 programmatic 修字 | `SKILL.md` L43 |
| Prompt 文件 hard requirement | `SKILL.md` L47 |
| Backend 解析顺序 | `SKILL.md` L28–L39 |
| 批量：native batch → 并行 tool → 顺序 | `SKILL.md` L51–L66 |
| image-1 锚定链（封面先出，后续 `--ref` 封面） | 同 SKILL 内 Visual consistency 段（约 L370+） |
| Session ID | Step 7 L301–L302 |

**跨 skill 图片 CLI**（若不用 Codex 原生 imagegen）：

- `references/baoyu-skills/skills/baoyu-image-gen/SKILL.md`
- `references/baoyu-skills/skills/baoyu-image-gen/scripts/main.ts` — 多 provider、batch file、`GOOGLE_API_KEY`/`OPENAI_API_KEY` 等
- `references/baoyu-skills/skills/baoyu-imagine/SKILL.md` — 另一 backend 选项

### 5.4 文件布局与备份（→ PRD Delivery）

```
slide-deck/{topic-slug}/
├── source-{slug}.{ext}
├── outline.md
├── prompts/NN-slide-{slug}.md
├── NN-slide-{slug}.png
├── {topic-slug}.pptx
└── {topic-slug}.pdf
```

出处：`SKILL.md` L204–L214。  
**备份规则**：写入前若存在则 `*-backup-YYYYMMDD-HHMMSS` — `SKILL.md` L218。→ 写入 `13-regeneration-workflow.md`。

### 5.5 其他高价值 reference

| 文件 | 用途 |
|------|------|
| `references/outline-template.md` | Slide Plan 字段、Typography 视觉描述（无字体名） |
| `references/layouts.md` | 每页 Layout 行 → Image prompt |
| `references/content-rules.md` | Writer 密度与禁忌 |
| `references/design-guidelines.md` | Designer 总则 |
| `references/modification-guide.md` | 迭代改 prompt/图 |
| `references/config/preferences-schema.md` | `EXTEND.md` 用户偏好 → 本项目用户 config |
| `references/dimensions/typography.md` | 图像模型用视觉字体描述 |

### 5.6 可执行脚本

| 脚本 | 路径 | 依赖 | PRD 用途 |
|------|------|------|----------|
| merge-to-pptx | `scripts/merge-to-pptx.ts` | Bun | Phase 2 可选导出 |
| merge-to-pdf | `scripts/merge-to-pdf.ts` | Bun | 同上 |

运行方式：`SKILL.md` L83–L84 — `${BUN_X}` = `bun` 或 `npx -y bun`。

---

## 6. 从 PRD 到实施的文件清单（建议新建）

以下路径以 PRD §7 信息架构为准；**「参考来源」列指向应阅读/移植的 refs 文件**。

### 6.1 主 Skill 与 References（流程骨架）

| 待建文件 | 参考来源 |
|----------|----------|
| `SKILL.md` | PRD §7.1、§14；ppt-master 管线铁律 `SKILL.md` L19–L27；guizang Step 1；baoyu Confirmation + 中间态 |
| `references/00-product-principles.md` | PRD §6；附录 A.4 |
| `references/01-intake-brief.md` | guizang `SKILL.md` L61–L71；baoyu `confirmation.md` Round 1 |
| `references/02-context-pack.md` | PRD §9 Step 2 结构；guizang 叙事弧 |
| `references/03-strategist.md` | ppt-master `references/strategist.md`；baoyu `analysis-framework.md` |
| `references/04-researcher.md` | ppt-master Step 1 整理；PRD Researcher §8.2 |
| `references/05-writer.md` | baoyu `content-rules.md`、`outline-template.md` |
| `references/06-reviewer.md` | guizang `checklist.md` 内容项；baoyu Step 4 |
| `references/07-designer.md` | ppt-master `design_spec_reference.md`；baoyu `design-guidelines.md` + `dimensions/` |
| `references/08-web-renderer.md` | guizang Step 2–3 全文；PRD §10 |
| `references/09-image-renderer.md` | baoyu `SKILL.md` Image Tools + Batch Policy；ppt-master `image-generator.md` |
| `references/10-style-guard.md` | guizang `checklist.md`；ppt-master Style Guard 概念 §8.8 |
| `references/11-producer.md` | PRD §9 Step 9；baoyu Step 9 |
| `references/12-style-presets.md` | baoyu `styles/` + `dimensions/presets.md`；guizang `themes*.md` |
| `references/13-regeneration-workflow.md` | baoyu `modification-guide.md`；`--regenerate` |
| `references/14-quality-checklist.md` | guizang `checklist.md`；ppt-master `svg_quality_checker` 检查项抽象 |
| `references/15-export-contract.md` | PRD Delivery 树；baoyu File Layout |

### 6.2 Assets

| 待建 | 优先参考 |
|------|----------|
| `assets/templates/web-slide-template.html` | guizang `assets/template.html`（抽离翻页内核，去 WebGL 可选） |
| `assets/templates/web-slide-template-minimal.html` | 同上 + 系统字体 |
| `assets/templates/image-prompt-template.md` | baoyu `base-prompt.md` + guizang `image-prompts.md` + PRD §11.3 |
| `assets/styles/*.css`（7 套） | guizang themes + baoyu preset 色彩语义 |
| `assets/style-presets/*.json` | baoyu dimensions 四维 + PRD §7.3 字段 |
| `assets/examples/*` | 自建；可参考 baoyu 示例 deck 结构 |

### 6.3 Scripts

| 待建 | 优先参考 |
|------|----------|
| `scripts/build_html.py` | 新写；输入 schema 见 PRD §9 Step 7B；模板填充逻辑参考 guizang「粘 layout 骨架」 |
| `scripts/validate_slide_plan.py` | ppt-master 结构检查思路；PRD §9 Step 4 字段 |
| `scripts/validate_context_lock.py` | ppt-master 每页读 spec_lock；PRD §12 |
| `scripts/generate_images.py` | 薄包装 `ppt-master/.../image_gen.py` 或调用 `baoyu-image-gen` |
| `scripts/export_images_manifest.py` | ppt-master `image_prompts.json` 状态字段 |
| `scripts/regenerate_slide.py` | baoyu `--regenerate` 语义 |
| `scripts/validate_html.py`（建议） | guizang `validate-swiss-deck.mjs` |

### 6.4 环境与配置

| 项 | 参考 |
|----|------|
| `.env.example` | `ppt-master` 的 `scripts/docs/image.md`；`baoyu-image-gen` `SKILL.md` env 列表 |
| Python 3 | ppt-master 全脚本 |
| Bun（可选） | baoyu merge 脚本 |
| Node（可选） | guizang `validate-swiss-deck.mjs` |

---

## 7. PRD 关键机制 → 三源合一实现说明

### 7.1 Image-first + HTML 自动接管

**逻辑编排借鉴**：

1. baoyu：backend 不可用 → 告知用户（`SKILL.md` L39）— 本项目改为 **自动切 HTML**（PRD §6.5）。
2. ppt-master：Step 5 `Needs-Manual` 仍继续 SVG，但导出门禁 — 借鉴「不阻断流程但标记缺口」(`image-base.md` §5)。
3. guizang：无图时用占位色块（`SKILL.md` L114）— HTML 路径可沿用。

**检测实现**：启动时跑 `generate_images.py --dry-run` 或检查 env → 写入 `context_pack.md` 的 `Output Mode` 字段。

### 7.2 Context Lock

| 字段类别 | ppt-master `spec_lock` | guizang | baoyu preset | PRD `style_lock.json` |
|----------|------------------------|---------|--------------|------------------------|
| 色板 | `colors.*` | `:root` in themes | mood/palette 叙述 | `primary_color` 等 |
| 字体 | `typography.*` | 模板 CSS 变量 | typography 维度 | `font_heading` / `font_body` |
| 画布 | `canvas.viewBox` | 16:9 section | 16:9 AR | `canvas_ratio` |
| 图风 | `image_rendering` | image-prompts 风格段 | texture+mood | `image_style` |
| 禁忌 | design_spec 叙述 | 硬约束 7 问 | content-rules | `forbidden[]` |

**执行纪律**：复制 ppt-master「每页渲染前 `read_file spec_lock`」→ 写入 `08-web-renderer.md`、`09-image-renderer.md`（PRD §12 使用规则）。

### 7.3 Prompt 作为资产

| 要求 | 最佳参考 |
|------|----------|
| 每页独立文件 | baoyu `prompts/NN-slide-{slug}.md` |
| 先落盘再调 API | ppt-master manifest 三步；baoyu Step 7.2 |
| 可切换 backend | baoyu L47；ppt-master `IMAGE_BACKEND` |
| 汇总索引 | ppt-master `image_prompts.md` sidecar；PRD `image_prompts.md` |

### 7.4 门禁（Gate 1–6）

| PRD Gate | 主要借鉴 |
|----------|----------|
| Gate 1 Brief | guizang 7 问 + baoyu Confirmation Round 1 |
| Gate 2 Outline | baoyu Step 4；ppt-master Strategist 大纲确认 |
| Gate 3 Content | baoyu review outline；Reviewer 角色 |
| Gate 4 Style | ppt-master Eight Confirmations 之 style/color/typography/image |
| Gate 5 Style Compliance | guizang checklist + validate script |
| Gate 6 Result Visible | baoyu Step 9；ppt-master 导出存在性检查 |

**BLOCKING 写法**：照抄 ppt-master `⛔ BLOCKING` 标记语法（`SKILL.md` L251）。

### 7.5 状态机（Agent 调度）

PRD §14.3：`brief → outline → plan → review → spec → render → qa → delivery`

| 状态 | 中间产物 | 参考 |
|------|----------|------|
| brief | `project_brief.md` | guizang 澄清结果 |
| outline | `outline.md` | baoyu Step 3 |
| plan | `slide_plan.json` | baoyu outline-template 扩展 |
| review | `review_report.md` | baoyu Step 4 输出 |
| spec | `design_spec.md` + `style_lock.json` | ppt-master Step 4 |
| render | `index.html` 和/或 `images/` | guizang + baoyu Step 7 |
| qa | `qa_report.md` | guizang checklist |
| delivery | PRD §9 目录树 | baoyu + PRD |

---

## 8. 实施阶段路线图（附参考优先级）

### Phase 0 — 契约（1–2 天）

- [ ] 从 baoyu `outline-template.md` 抽出 `slide_plan.schema.json`
- [ ] 从 ppt-master `spec_lock_reference.md` + PRD §12 合并 `style_lock.schema.json`
- [ ] 写 `references/00`–`02`（原则、intake、context-pack）
- [ ] `.env.example` 抄 `ppt-master/scripts/docs/image.md` 的 gemini/openai 段

### Phase 1 — HTML 闭环（先保证 Gate 6）

- [ ] 拷贝改造 guizang `template.html` → `web-slide-template.html`（1 套 teaching-clean）
- [ ] 从 `layouts.md` 抽 5–6 种最常用 layout → `build_html.py` 占位符
- [ ] 流程跑通：brief → outline → plan → spec → `index.html`
- [ ] 移植 `checklist.md` 要点 → `14-quality-checklist.md`

### Phase 2 — Image 闭环

- [ ] `image-prompt-template.md` = baoyu `base-prompt.md` + PRD §11.3 字段
- [ ] `generate_images.py` 包装 `ppt-master/scripts/image_gen.py`
- [ ] 实现 `prompts-only` / `images-only` / `regenerate`（语义照抄 baoyu CLI）
- [ ] `export_images_manifest.py` 对齐 ppt-master manifest 状态

### Phase 3 — 完整 v1

- [ ] 7 presets（从 baoyu 17 + guizang 2 映射，见 §12-style-presets.md）
- [ ] Image-first + 自动 HTML takeover
- [ ] Mixed：HTML 引用 `images/slide-NN.png`（guizang 图片路径约定）
- [ ] 16 篇 references 补齐
- [ ] 可选：`merge-to-pptx.ts` 从 baoyu 复制改路径

---

## 9. 快速路径索引（按「我要实现 X」查找）

| 我要实现… | 先打开 |
|-----------|--------|
| 需求澄清问卷 | `guizang-ppt-skill/SKILL.md` L61–L71 |
| 用户确认 UI 文案 | `baoyu-slide-deck/references/confirmation.md` |
| 叙事弧 / 页数规划 | `guizang-ppt-skill/SKILL.md` L87–L97 |
| 逐页大纲字段 | `baoyu-slide-deck/references/outline-template.md` |
| 设计规格文档结构 | `ppt-master/skills/ppt-master/templates/design_spec_reference.md` |
| 机器可读风格锁 | `ppt-master/.../templates/spec_lock_reference.md` |
| HTML 模板与翻页 | `guizang-ppt-skill/assets/template.html` |
| 页面 layout 骨架 | `guizang-ppt-skill/references/layouts.md` |
| 主题色 CSS 变量 | `guizang-ppt-skill/references/themes.md` |
| 图片 Prompt 正文模板 | `baoyu-slide-deck/references/base-prompt.md` |
| 图片 API 调用 | `ppt-master/skills/ppt-master/scripts/image_gen.py` |
| 图片 env 配置说明 | `ppt-master/skills/ppt-master/scripts/docs/image.md` |
| 禁止假图/假字规则 | `baoyu-slide-deck/SKILL.md` L41–L47 |
| 批量出图与重试 | `baoyu-slide-deck/SKILL.md` L51–L66 |
| 管线串行与 GATE | `ppt-master/skills/ppt-master/SKILL.md` L19–L27 |
| 出图后合并 PPTX | `baoyu-slide-deck/scripts/merge-to-pptx.ts` |
| 瑞士风 HTML 校验 | `guizang-ppt-skill/scripts/validate-swiss-deck.mjs` |
| 生产踩坑清单 | `guizang-ppt-skill/references/checklist.md` |

---

## 10. 许可与拷贝注意

- **ppt-master**：MIT（仓库根 `LICENSE`）
- **guizang-ppt-skill**：见 `references/guizang-ppt-skill/LICENSE`
- **baoyu-skills**：见 `references/baoyu-skills/LICENSE`（slide-deck 为子目录）

拷贝代码或全文模板时保留版权声明；`guizang` 的 provenance 注释（`SKILL.md` L8、L34）要求**不要**写入最终用户交付物——写入本 Skill 的 `SKILL.md` 即可。

---

## 11. 文档维护

| 字段 | 值 |
|------|-----|
| 版本 | v1.0 |
| 对应 PRD | `ai_slide_producer_prd_v1.md` v1.0 |
| 参考快照日期 | 2026-05 |
| 下次更新触发 | refs 子模块升级、PRD 升版、本项目 `assets/`/`scripts/` 首次落地后回填「已实现」列 |

---

**关联文档**：`ai_slide_producer_prd_v1.md`（产品定义）· `references/`（只读上游样本，不直接修改）
