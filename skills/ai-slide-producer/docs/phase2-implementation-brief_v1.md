# Phase 2 实施 Brief v1

> **读者**：Phase 2 执行者（可独立实施，不必通读根目录主 PRD）  
> **状态**：建议稿 — 执行者可在本文 §5 拍板后开工  
> **契约来源**：[`SKILL.md`](../SKILL.md) Step 7A/7C、[`references/15-export-contract.md`](../references/15-export-contract.md)、[`schemas/image_prompts.schema.json`](../schemas/image_prompts.schema.json)

---

## 1. 目标（一句话）

把 **7A-P Prompt Staging** 做成可脚本回归的流水线；**7A-G 真出图** 第二刀再接，全程遵守「Prompt 是资产、禁止伪图、backend 不可用不伪造」。

Phase 1 已具备：`build_html.py`、`teaching-clean-demo`（`slide_plan.json` + `style_lock.json` → `index.html`）。Phase 2 **不破坏** HTML 路径。

---

## 2. 两刀交付顺序（建议采纳）

| 刀 | 范围 | 验收核心 |
|----|------|----------|
| **第一刀** | Prompt Staging 可跑 | `export_images_manifest.py` 从现有 demo 产出 `prompts/` + `images_manifest.json`（+ 可选 `source/image_prompts.md`），**无需 API Key** |
| **第二刀** | Backend + 重生 | `generate_images.py` 读 manifest 真出图；`regenerate_slide.py`；文档 `09` / `13` 与中间态 CLI 对齐 |

**第一刀刻意不做**：OpenAI/Gemini 调用、占位 PNG、SVG/HTML 冒充 raster。

**第二刀刻意要做**：无 key 或 backend 不可用时条目保持 `pending` / `needs-manual`，写清错误，**不伪造图片**。

---

## 3. 交付物清单（与执行者方案对齐）

### 文档（Phase 2）

| 文件 | 职责 |
|------|------|
| `references/09-image-renderer.md` | 7A-P / 7A-G、Prompt Staging、backend、失败状态、禁止伪图、**每页生成前重读 `style_lock.json`** |
| `references/13-regeneration-workflow.md` | `prompts-only` / `images-only` / `regenerate N`、备份规则、manifest 状态流转 |
| `assets/templates/image-prompt-template.md` | 单页 Prompt 稳定模板，字段与 `image_prompts.schema.json` frontmatter 对齐 |

### 脚本（Phase 2）

| 脚本 | 建议刀次 | 职责 |
|------|----------|------|
| `scripts/export_images_manifest.py` | **第一刀** | 读 `<project>/source/slide_plan.json` + `style_lock.json` → 写 `prompts/NN-slide-{slug}.md`、`images_manifest.json`、可选 `source/image_prompts.md` |
| `scripts/generate_images.py` | **第二刀** | 薄封装：读 manifest，按 `image_backend` 调 API；失败 → `needs-manual`，继续后续页 |
| `scripts/regenerate_slide.py` | **第二刀** | 指定页重生：备份旧 prompt/image，更新 manifest，**只处理目标页** |

命名与目录树以 [`15-export-contract.md`](../references/15-export-contract.md) 为准（`slide-NN.png`、`NN-slide-{slug}.md`）。

---

## 4. `export_images_manifest.py` 职责折中（需执行者定稿）

主 PRD / SKILL 字面是 Agent **逐页派生** Image Prompt；执行者方案是脚本从 plan + lock **批量脚手架**。二者不矛盾，推荐写成 **混合模式**（默认，除非你在 §5 选 B）：

```
slide_plan + style_lock + image-prompt-template.md
        ↓ export_images_manifest.py（机械 baseline）
   prompts/NN-slide-{slug}.md  +  images_manifest.json
        ↓（可选）Agent / 人在 Gate 4 后润色 prompts/*.md
        ↓ generate_images.py（第二刀，仅 image-first / mixed 且 backend 可用）
   images/slide-NN.png
```

| 模式 | export 脚本 | Agent |
|------|-------------|-------|
| **A 脚手架 + 可编辑（推荐）** | 生成 frontmatter + baseline `visual_composition`（来自 plan 的 `key_message` / layout / `image_requirement` 等） | 复杂页、金句页、Mixed 指定页可改 markdown 正文后再跑 generate |
| **B 仅 manifest** | 只扫已有 `prompts/` 或只写 manifest 骨架 | Prompt 正文 100% Agent 手写；export 不覆盖已有 `.md` |
| **C 强制覆盖** | 每次 export 覆盖 prompts（适合纯回归） | 不适合生产项目，仅 CI/gallery |

**第一刀默认行为建议**：

- 若 `prompts/` 不存在 → 创建全套 baseline。
- 若已存在且未传 `--force` → **不覆盖**正文（只更新 manifest 中路径/状态/backend 字段）；传 `--force` 才重写（与 `15-export-contract` 备份语义衔接，见 `13` 文档）。

---

## 5. 执行者拍板（已确认，2026-05-21）

| 项 | 决议 |
|----|------|
| Prompt 来源 | **模式 A**：脚手架 + 可编辑（`export_images_manifest.py` 生成 baseline，无 `--force` 不覆盖正文） |
| `image_prompts.md` | **第一刀必生成**（`source/image_prompts.md`） |
| `generate_images.py` | **第一刀不实现**；不占位图、不伪造 raster |

2a 验收：demo 4 prompt / gallery 10 prompt；manifest 全 `pending`，`default_backend: none`；二次 export `kept` 已有 prompt。

2b/2c（已落地）：`generate_images.py`（OpenAI/Gemini 同步出图；网关需 User-Agent）、`regenerate_slide.py`、`13-regeneration-workflow.md`。laogouapi 异步 Jobs 见 `09` §同步 vs 异步。

---

## 6. 第一刀验收命令（建议写进 PR）

在 `skills/ai-slide-producer/` 下：

```bash
python3 -m py_compile scripts/export_images_manifest.py

python3 scripts/export_images_manifest.py assets/examples/teaching-clean-demo

# 期望产物（路径相对 demo 项目根）：
#   prompts/*.md          — 页数 = slide_plan pages 中需 image 的页（见 plan.image_requirement）
#   images_manifest.json  — 通过 schema 校验；无 key 时 backend=none 或 status=pending
# 可选：
#   source/image_prompts.md

# 建议补充（执行者实现 validate 脚本或复用现有工具）：
# python3 scripts/validate_images_manifest.py assets/examples/teaching-clean-demo
```

**通过标准**：

- [ ] 不调用任何图片 API
- [ ] 不生成 `images/slide-*.png`（除非目录已有人工图，export 不伪造）
- [ ] manifest 与每页 prompt frontmatter 字段齐全（`style_lock_ref` 指向 `source/style_lock.json`）
- [ ] `html-takeover` 语义：对应页 manifest `status` 为 `pending`，`image_backend` 可为 `none`

---

## 7. 第二刀验收要点（简表）

- [ ] `.env` 有 key 时：`generate_images.py <project>` 写出 `images/slide-NN.png` 并回写 manifest `status: done`（或项目约定成功态）
- [ ] 无 key：保持 `pending`，进程 exit 0 或明确 warning，**exit 非 0 仅用于配置错误**
- [ ] `regenerate_slide.py <project> 3`（或 `3,5`）备份旧文件、只更新指定页
- [ ] `prompts-only` / `images-only` 与 SKILL Step 7C 表一致
- [ ] 禁止：代码绘制 bitmap 修字、SVG/HTML/Canvas 当 PNG

上游参考（实现时可抄语义，不必抄路径）：

- Prompt 正文结构：`references/baoyu-skills/.../base-prompt.md`（仓库 `references/`）
- API 薄包装：`references/ppt-master/.../image_gen.py`
- CLI 中间态：`references/baoyu-skills/.../slide-deck` 的 `--regenerate` / `prompts-only`

---

## 8. 与 Phase 1 / 其它任务边界

| 任务 | 关系 |
|------|------|
| `teaching-clean-layout-gallery` | **已完成**（`8c17e62`）；Phase 2 第一刀可用其作 `export_images_manifest` 回归输入 |
| Phase 3 Style Guard / 7 preset 全套 | **不在** Phase 2 范围 |
| `build_html.py` | Phase 2 不改契约；Mixed 第二刀后 HTML 引用 `images/slide-NN.png` 可另开小 PR |

---

## 9. 建议 PR 拆分（执行者可调整）

1. **PR-2a**：`image-prompt-template.md` + `export_images_manifest.py` + `09` 中 7A-P 章节 + demo 跑通第一刀验收  
2. **PR-2b**：`generate_images.py` + `09` 中 7A-G + `.env.example` 说明  
3. **PR-2c**：`13-regeneration-workflow.md` + `regenerate_slide.py` + CLI 中间态  

也可 2a+2b 合并，但 **2a 必须先可独立合并**。

---

## 10. 修订记录

| 版本 | 日期 | 说明 |
|------|------|------|
| v1 | 2026-05-21 | 产品方与执行者方案对齐：两刀 + export 脚手架折中 |
