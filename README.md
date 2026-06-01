# AI Slide Producer

> 把粗糙输入变成可见 Slides 结果的 AI 生产系统——Image 与 HTML 双输出，每一步都有人工门禁，每页 Prompt 都是可复用资产。

| 文档 | 用途 |
|------|------|
| [`ai_slide_producer_prd_v1.md`](ai_slide_producer_prd_v1.md) | 产品需求定义（PRD v1.0） |
| [`ai_slide_producer_implementation_guide_v1.md`](ai_slide_producer_implementation_guide_v1.md) | 参考实施指导（从 PRD 倒推「要建什么、从哪抄什么」） |
| [`skills/ai-slide-producer/SKILL.md`](skills/ai-slide-producer/SKILL.md) | 主 Skill 入口（触发、状态机、Gate、管线铁律） |
| [`references/`](references/) | 上游样本（只读，不修改） |

---

## 当前状态

**Phase 1：HTML 闭环 — 已完成第一版 ✅**

已完成：

- `skills/ai-slide-producer/SKILL.md` — 主 Skill：触发词、状态机、6 Gate、9 步管线、Output Mode 探测时机
- `skills/ai-slide-producer/references/`
  - `00-product-principles.md` — PRD §6 八条原则的可执行版
  - `01-intake-brief.md` — Step 1 / Gate 1 / 8 问清单 / Round 1 确认 UX
  - `02-context-pack.md` — Step 2 / 7 套 Preset 一对一映射表 / Output Mode 探测细则
  - `15-export-contract.md` — Step 9 / 三种交付目录树 / 文件命名 / `build_html.py` 拼装策略
- `skills/ai-slide-producer/schemas/`
  - `slide_plan.schema.json` — 逐页计划 JSON Schema
  - `style_lock.schema.json` — 风格锁 JSON Schema（PRD §12 + ppt-master spec_lock 合并）
  - `image_prompts.schema.json` — 单页 Prompt frontmatter + manifest 双 schema
- `skills/ai-slide-producer/.env.example` — 图片 backend 环境变量模板（openai / gemini core tier + 扩展）
- Phase 0.5 契约修补：`html-takeover` Prompt Staging、Output Mode 落盘时机、Manifest backend enum、HTML escaping、slide plan 语义校验约束
- Phase 1 HTML 闭环：
  - `references/06-reviewer.md`、`07-designer.md`、`08-web-renderer.md`、`14-quality-checklist.md`
  - `assets/templates/web-slide-template.html`、`web-slide-template-minimal.html`
  - `assets/templates/layouts/*.html.snippet`（10 种 PRD 页面类型）
  - `assets/styles/teaching-clean.css`
  - `assets/style-presets/teaching-clean.json`
  - `scripts/build_html.py`、`validate_slide_plan.py`、`validate_context_lock.py`、`validate_html.py`
  - `assets/examples/teaching-clean-demo/` 回归样例，已生成 `index.html`

本轮在写作中**直接落字解决**了 4 处对齐项：

1. **Reviewer 返工策略**（SKILL.md §Step 5）：自动重写最多 1 轮，超过回退到 Gate 2 由用户重审。
2. **7 套 Preset 一对一映射表**（`02-context-pack.md` §Preset 一对一映射表）：每套 preset 唯一绑定到上游样本源文件。
3. **Output Mode 探测时机**（SKILL.md / `02-context-pack.md`）：固定在 Step 1 Intake 收尾，结果先写入 `project_brief.md`，Step 2 再复制到 `context_pack.md`。
4. **`build_html.py` 拼装策略**（`15-export-contract.md` §build_html.py 拼装策略）：模板 + 占位符替换 + layout snippet 拼接，不引入模板引擎。

---

## 下一阶段（Phase 2：Image 闭环）

目标：在 Phase 1 HTML 可见结果基础上，补齐 Image Prompt 资产化、图片 backend 包装、中间态续生和局部重生。

预计新增：

- `references/09-image-renderer.md`
- `references/13-regeneration-workflow.md`
- `assets/templates/image-prompt-template.md`
- `scripts/generate_images.py`
- `scripts/export_images_manifest.py`
- `scripts/regenerate_slide.py`

---

## 后续阶段速览

| Phase | 主目标 | 主要新增 |
|-------|--------|----------|
| Phase 2 | Image 闭环 + 中间态 | `09-image-renderer.md`、`13-regeneration-workflow.md`、`generate_images.py`、`export_images_manifest.py`、`regenerate_slide.py`、`assets/templates/image-prompt-template.md` |
| Phase 3 | 完整 v1 | 剩余 references（03/04/05/10/11/12）、7 套 preset 的完整 CSS+JSON、Style Guard、可选 PPTX 导出 |

---

## 仓库结构

```
jumpx-ppt-slides-skill/
├── README.md                                       # 本文件
├── ai_slide_producer_prd_v1.md                     # PRD
├── ai_slide_producer_implementation_guide_v1.md    # 实施指导
├── skills/
│   └── ai-slide-producer/                          # Skill 本体
│       ├── SKILL.md
│       ├── .env.example
│       ├── references/
│       │   ├── 00-product-principles.md
│       │   ├── 01-intake-brief.md
│       │   ├── 02-context-pack.md
│       │   └── 15-export-contract.md
│       └── schemas/
│           ├── slide_plan.schema.json
│           ├── style_lock.schema.json
│           └── image_prompts.schema.json
└── references/                                     # 上游样本（只读）
    ├── baoyu-skills/
    ├── guizang-ppt-skill/
    └── ppt-master/
```

---

## 快速上手（Phase 0 阶段的可做事项）

当前可做：

- **审阅契约**：通读 `skills/ai-slide-producer/SKILL.md` + 4 篇 references + 3 份 schema，验证产品骨架是否符合预期。
- **用 schema 验证手写产物**：手工写一份 `slide_plan.json` 草稿，用 JSON Schema 工具校验 schema 是否覆盖所需字段。
- **review 4 处对齐项落地是否合理**：见 `00-product-principles.md`、`02-context-pack.md`、`15-export-contract.md`、SKILL.md。

尚不能做（需 Phase 1+）：

- 实际生成 HTML / 图片（无 build_html、无模板）
- 调用图片 backend（无 generate_images 脚本）

---

## License

- 本仓库代码与文档：见根目录 LICENSE（待补，建议 MIT）
- 上游样本许可：
  - `references/ppt-master/` — MIT
  - `references/guizang-ppt-skill/` — 见其 LICENSE
  - `references/baoyu-skills/` — 见其 LICENSE

拷贝上游模板/代码到 `skills/ai-slide-producer/assets/` 或 `scripts/` 时必须保留原版权头。
