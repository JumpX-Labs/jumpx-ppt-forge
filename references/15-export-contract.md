# 15 — Export Contract

> Step 9 落地文档。三种最终交付目录树、文件命名规则、HTML 渲染契约（模型直接写）。

---

## 角色

> 切换到 **Producer**。

职责：

- 整理最终目录、统一命名。
- 写项目级 `README.md`（用户可见，说明怎么打开/改/重生）。
- 把 `qa_report.md` 关键结论 surface 到 README 顶部。
- 在交付前确认 **结果可见**（至少有可打开的 `index.html` 或首张 `images/slide-01.*`）。

---

## 三种交付目录树

`<project>` = `<topic-slug>`（kebab-case，最长 50 字符）。

### Mixed 输出（HTML + Image 都给）

```
<project>/
├── README.md                       # 用户视角的说明（必）
├── index.html                      # 单页 HTML，本地可打开
├── images/
│   ├── slide-01.png
│   ├── slide-02.png
│   └── ...
├── prompts/
│   ├── 01-slide-cover.md
│   ├── 02-slide-{slug}.md
│   └── ...
├── images_manifest.json            # 每页 prompt 路径、图片路径、backend、状态
├── source/
│   ├── project_brief.md
│   ├── context_pack.md
│   ├── outline.md
│   ├── slide_plan.json
│   ├── design_spec.md
│   ├── style_lock.json
│   ├── review_report.md
│   └── image_prompts.md            # prompts/ 的人类可读汇总，便于阅读
└── qa_report.md
```

Mixed 验收步骤：

1. `source/slide_plan.json.deck_meta.output_mode` 必须为 `mixed`。
2. 至少 1 页 `image_requirement.needed == true`；训练营样例建议 2-3 页。
3. 有图页的文件位于 `images/slide-NN.png` / `.jpg` / `.jpeg` / `.webp`。
4. HTML 必须在图片生成或本地占位图准备之后再渲染。
5. `index.html` 中对应页出现 `<img src="images/slide-NN...">`；缺图时出现 `Image pending (slide-NN)`，不得出现断裂图片。
6. `qa_report.md` 记录图片状态；manifest pending 可 warning，但 HTML 可见不应阻塞交付。

### HTML-only（含 html-takeover、html-only、html-only-with-prompts）

```
<project>/
├── README.md
├── index.html
├── source/
│   ├── project_brief.md
│   ├── context_pack.md
│   ├── outline.md
│   ├── slide_plan.json
│   ├── design_spec.md
│   ├── style_lock.json
│   └── review_report.md
├── prompts/                        # 仅 html-takeover / html-only-with-prompts 才有
│   └── ...
├── images_manifest.json            # 仅有 prompts 时存在；状态字段全为 pending
└── qa_report.md
```

### Image-only（用户显式只要 Image）

```
<project>/
├── README.md
├── images/
│   └── slide-NN.png
├── prompts/
│   └── NN-slide-{slug}.md
├── images_manifest.json
├── source/
│   ├── project_brief.md
│   ├── context_pack.md
│   ├── outline.md
│   ├── slide_plan.json
│   ├── design_spec.md
│   ├── style_lock.json
│   └── review_report.md
└── qa_report.md
```

---

## 文件命名规则

| 类型 | 规则 | 示例 |
|------|------|------|
| 项目根目录 | `<topic-slug>` kebab-case，最长 50 字符 | `ai-course-intro-q2/` |
| 幻灯片图片 | `slide-NN.png`，N 零填充到 2 位 | `slide-01.png`, `slide-12.png` |
| 单页 Prompt | `NN-slide-{slug}.md`，slug ≤ 30 字符 | `01-slide-cover.md`, `07-slide-key-takeaway.md` |
| Manifest | `images_manifest.json`（固定名） | — |
| 项目 README | `README.md`（固定名） | — |
| QA 报告 | `qa_report.md`（固定名） | — |
| 中间产物 | 全部固定名见 SKILL.md §状态机 | — |

**Slug 生成**：

- 全小写、kebab-case（连字符分词）
- 来自该页 `key_message` 或 `page_title` 的关键词
- 去除停用词（the / a / 的 / 是 / 在 等）
- 同 deck 内必须唯一；冲突时追加 `-2`、`-3`

**封面 / 封底固定 slug**：

- 第 1 页：`cover` → `01-slide-cover.md` / `slide-01.png`
- 末页（若有总结/感谢）：`back-cover` → `NN-slide-back-cover.md`

---

## 备份规则（写入前若存在）

当 regenerate 或重跑覆盖文件时：

```
<original-name>-backup-YYYYMMDD-HHMMSS.<ext>
```

适用范围：`index.html`、`slide-NN.png`、`NN-slide-{slug}.md`、`source/*`、`images_manifest.json`、`qa_report.md`。

不要备份的：`README.md`（始终重写）、临时 cache。

---

## 项目 README.md 模板（必写）

```markdown
# <topic 中文/英文标题>

<1 句话定位>

---

## 怎么看

- **HTML**：双击 `index.html` 即可在浏览器打开。键盘 ←→ 翻页，ESC 缩略图索引。
- **Image**：见 `images/`，按文件名顺序浏览。

## 这次交付包含

- [ ] 完整 HTML deck（N 页）
- [ ] N 张 slide images
- [ ] N 个 image prompts（位于 `prompts/`）
- [ ] 源数据（`source/`）、QA 报告（`qa_report.md`）

## QA 摘要

<从 qa_report.md 抓 3 行关键结论>

## 怎么改

- 改文字：编辑 `source/slide_plan.json` 后，让 Web Renderer 按 08 契约重写 `index.html`。
- 改风格：回到 Gate 4 修改 `source/style_lock.json`，再重新渲染。
- 局部重生：运行 `python3 scripts/regenerate_slide.py <project> PNN`。

## 怎么续生（image-only / html-takeover 场景）

如果当前只有 prompts 没有图片：

1. 配置图片 backend（参考 Skill 内 `ai-slide-producer/.env.example`）
2. 跑 `images-only` 模式，会从 `prompts/` 批量生成 → `images/`

## 元数据

- Output Mode: <image-first | html-only | mixed | ...>
- Style Preset: <style_name>
- Backend used: <openai | gemini | native | none>
- Generated: YYYY-MM-DD HH:mm
```

---

## HTML 渲染契约（模型直接写）

HTML 由 Web Renderer（模型）按 [`08-web-renderer.md`](08-web-renderer.md) **直接编写 `index.html`**（无模板拼装、无 layout snippet）。本节只列与"交付"相关的硬性约束。

**产物**：`<project>/index.html` —— 完全自包含、CSS/JS 全内联、可双击打开、16:9 横向翻页。

**结构契约**（演示/导出依赖）：

- `<main id="deck">` 内每页一个 `<section class="slide" data-page-id="P01" data-layout="...">`；slide 数 = `deck_meta.total_pages`。
- 切页 `deck.style.transform = translateX(-i*100vw)`；含键盘 ←→ / 触摸 / ESC 缩略图索引。
- `speaker_notes` 放进 `<aside class="notes" hidden>`，不影响视觉。

**安全 / 转义（模型必须遵守）**：

- 来自用户/LLM 的文本（标题/要点/备注/caption）按 HTML 文本安全处理，不得注入可执行内容。
- 可见图片只允许本项目相对路径白名单 `images/slide-NN.{png,jpg,jpeg,webp}`；禁止外链 `http(s)://` / `data:` / `javascript:` 或任意用户输入路径。
- 全内联、不引任何外部资源（CDN / 外链字体 / 远程脚本）。

**validate_slide_plan.py 语义检查（JSON Schema 之外）**：

- `deck_meta.total_pages == len(pages)`
- `page_id` 唯一、连续、从 `P01` 开始，并与数组顺序一致
- `layout_type` 取值在已知集合内（作为版面建议；不要求存在模板文件）
- `deck_meta.style_name` 与 `source/style_lock.json.style_name` 一致（当 style lock 已存在）
- `image_requirement.text_in_image_risk == "high"` 时给 warning，提示优先 HTML 或减少可见文字

**validate_html.py**：检查 `index.html` 存在、有 `#deck` + 正确数量的 `.slide`、含翻页/索引脚本、无残留 `{{...}}` 占位符、自包含无外链。

---

## Producer 交付前检查清单

按顺序勾选：

- [ ] 目录结构与上述三种树之一完全一致
- [ ] `index.html` 双击可打开（如有），无 console error
- [ ] `images/` 数量 = `slide_plan.json` 中 `image_requirement=true` 的页数（如适用）
- [ ] 每张图都有对应 `prompts/NN-*.md`
- [ ] `images_manifest.json` 与实际文件一致（无 dangling 引用）
- [ ] `source/*` 全部存在且通过 schema 验证
- [ ] `qa_report.md` 无 critical issue（或已在 README 中标注 known issues）
- [ ] `README.md` 写完，包含"怎么看 / 怎么改 / 怎么续生"
- [ ] 结果可见：至少有 `index.html` 或 `images/slide-01.png`

**Gate 6 Result Visible**：上述全勾才允许告诉用户"交付完成"。

---

## 与其他角色的衔接

| 上一步 | 谁交给 Producer 什么 |
|--------|---------------------|
| Step 7A Image Renderer | `images/` + `prompts/` + `images_manifest.json` |
| Step 7B Web Renderer | `index.html` |
| Step 8 Quality Check | `qa_report.md` |
| Step 6 Designer | `design_spec.md` + `style_lock.json` |
| Step 4 Writer | `slide_plan.json`（用于 README 元数据） |

Producer 不修改任何上游产物；只整理位置 + 写 README + 写交付摘要。

---

**关联文档**：
- [`00-product-principles.md`](00-product-principles.md)
- [`11-producer.md`](11-producer.md)
- [`SKILL.md`](../SKILL.md) — 状态机、Gate 6
- [`../schemas/slide_plan.schema.json`](../schemas/slide_plan.schema.json)
- [`../schemas/image_prompts.schema.json`](../schemas/image_prompts.schema.json)
