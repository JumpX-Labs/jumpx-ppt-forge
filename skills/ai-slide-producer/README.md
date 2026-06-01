# AI Slide Producer（Skill 包）

> 把粗糙输入变成**可见 Slides 结果**的 Agent Skill：网页幻灯片、配图或二者兼有；关键步骤需你确认；每页图片 Prompt 可单独保存复用。

本目录是 **Git 仓库根**（`skills/`）。在 Cursor / CraftAgents 中安装或引用 `ai-slide-producer/` 即可使用。

---

## 你能做什么（v1.0）

| 能力 | 说明 |
|------|------|
| 九步管线 | 需求澄清 → 大纲 → 逐页计划 → 审核 → 定风格 → 出图/出网页 → 质检 → 交付 |
| 输出形态 | `html-only`（推荐上课）、`image-first`、`mixed`（网页 + 部分配图） |
| 7 套视觉风格 | 默认 `teaching-clean`；对外展示常用 `editorial-magazine` |
| 脚本拼装 HTML | Agent **不得**手写 `index.html`，须运行 `scripts/build_html.py` |
| 真实出图 | 配置 `.env` 后 `generate_images.py`（OpenAI / Gemini 等）；无 Key 时自动改网页并保留 Prompt |

触发词与完整流程见 [`SKILL.md`](SKILL.md)。

---

## 快速入口

| 你想… | 打开 |
|--------|------|
| **在 Agent 里怎么用** | [`SKILL.md`](SKILL.md) |
| 需求澄清（Step 1） | [`references/01-intake-brief.md`](references/01-intake-brief.md) |
| 风格怎么选 | [`references/12-style-presets.md`](references/12-style-presets.md) |
| 生成网页（Step 7B） | [`references/08-web-renderer.md`](references/08-web-renderer.md) |
| 导出图片 Prompt / 出图（Step 7A） | [`references/09-image-renderer.md`](references/09-image-renderer.md) |
| 交付目录长什么样 | [`references/15-export-contract.md`](references/15-export-contract.md) |
| 跑回归样例 | [`assets/examples/README.md`](assets/examples/README.md) |
| 配置图片 API | [`.env.example`](.env.example)（复制为 `.env`，勿提交密钥） |

**维护者与 QA**：验收勾选、实施记录见 [`docs/`](docs/)（Agent 不必读）。

---

## 目录结构

```text
ai-slide-producer/
├── SKILL.md                  # Agent 主入口
├── references/               # 各 Step 角色手册（00–15）
├── schemas/                  # JSON Schema
├── assets/templates|styles|style-presets|examples/
├── scripts/                  # build_html、出图、校验、重生
└── docs/                     # UAT 与实施记录（维护者）
```

---

## 本机冒烟（HTML）

在 `skills/ai-slide-producer/` 下：

```bash
python3 scripts/build_html.py assets/examples/teaching-clean-demo
python3 scripts/validate_html.py assets/examples/teaching-clean-demo/index.html
```

浏览器打开对应 `index.html`（← → 翻页，ESC 缩略图）。更多样例命令见 [`assets/examples/README.md`](assets/examples/README.md)。

出图（需 `.env`）：

```bash
python3 scripts/probe_image_backend.py assets/examples/teaching-clean-demo
python3 scripts/generate_images.py assets/examples/teaching-clean-demo --backend openai --only P01
```

---

## 许可

内置模板与风格资产含开源版权头；拷贝到 `assets/` / `scripts/` 时须保留。**用户交付的 deck 里不写 provenance 说明。**

---

<details>
<summary>维护者：版本与开发批次（点击展开）</summary>

| 批次 | 状态 | 要点 |
|------|------|------|
| 契约 + HTML | 已完成 | `SKILL.md`、schemas、`build_html.py`、10 layout |
| 出图 + 重生 | 已完成 | `export_images_manifest.py`、`generate_images.py`、`regenerate_slide.py` |
| 叙事 + 视觉 | 已完成 | references 03–05、7 preset、Style Guard / Producer |
| v1.0 收口 | 已完成 | UAT 表、固定样例、nanobanana backend |

Git 历史见 `skills/` 仓库 log；上级 monorepo 产品 PRD 在 `../../`（只读）。

</details>
