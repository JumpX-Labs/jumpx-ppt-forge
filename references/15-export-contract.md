# 15 — Export Contract

> Step 9 落地文档。三种最终交付目录树、文件命名规则、build_html 拼装策略。

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
4. `build_html.py` 必须在图片生成或本地占位图准备之后运行。
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

- 改文字：编辑 `source/slide_plan.json` 后重新运行 `python3 scripts/build_html.py <project>`。
- 改风格：回到 Gate 4 修改 `source/style_lock.json`，再重跑 HTML / Image。
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

## build_html.py 拼装策略

**决策**：模板 + 占位符替换 + layout snippet 拼接。**不引入模板引擎**（Jinja / Mustache / Handlebars 均不用）；仅依赖 Python 标准库与仓库内脚本，无需 npm 构建。

**输入**：

```
slide_plan.json
style_lock.json
context_pack.md（可选，用于 README）
assets/templates/web-slide-template.html
assets/templates/web-slide-template-minimal.html（系统字体回退版）
assets/styles/<style_name>.css
assets/templates/layouts/<layout_type>.html.snippet（每种 layout 一个 snippet）
```

**输出**：

```
<project>/index.html        # 完全自包含；CSS 内联；可双击打开
```

**拼装步骤**：

```
1. read style_lock.json
2. read template = assets/templates/web-slide-template.html
3. inline CSS:
   read assets/styles/<style_name>.css
   substitute :root vars from style_lock (primary_color, accent_color, font_*, density tokens)
   write into template's <style> block
4. for each page in slide_plan.json:
     snippet = read assets/templates/layouts/<page.layout_type>.html.snippet
     fill placeholders: {{page_title}}, {{key_message}}, {{on_slide_text}}, etc.
     if page.image_requirement.generated_image_path exists and file is present:
        substitute {{image_block}} = <img src="that path">
     else if images/slide-NN.{png,jpg,jpeg,webp} exists:
        substitute {{image_block}} = <img src="images/slide-NN.ext">
     else if page.image_requirement.needed is true:
        substitute {{image_block}} = Image pending (slide-NN)
     else:
        substitute {{image_block}} = no-image text placeholder
     append <section data-page-id="..." data-layout="..."> ... </section>
5. inject inline JS for keyboard/swipe/ESC index (one-time copy from web-slide-template.html bottom <script>)
6. write index.html
```

**Layout snippet 命名约定**：

```
assets/templates/layouts/
├── cover.html.snippet
├── section-divider.html.snippet
├── big-idea.html.snippet
├── two-column.html.snippet
├── quote.html.snippet
├── framework.html.snippet
├── timeline.html.snippet
├── comparison.html.snippet
├── image-text.html.snippet
└── closing.html.snippet
```

10 种页面类型与 `slide_plan.json` 的 `layout_type` 一一对应；每种是一个**纯 HTML 片段**（无 `<html>` / `<head>` 外壳），里面用 `{{...}}` 占位。

**占位符规则**：

- `{{page_title}}` → `page.page_title`
- `{{key_message}}` → `page.key_message`
- `{{on_slide_text}}` → `page.on_slide_text`，多行用 `\n\n` 分段
- `{{image_src}}` → `page.image_requirement.generated_image_path`、`images/slide-NN.png` 或空（没图时片段须能优雅退化为占位色块）
- `{{image_block}}` → 完整 `<img src="images/slide-NN.ext">` 或明确占位；只有 layout snippet 可决定它出现在哪里
- `{{speaker_notes}}` → 写入 `<aside class="notes" hidden>`，不影响视觉
- `{{page_role}}` → `data-role` 属性，便于 CSS 区分 cover / divider / content
- 不出现在 slide_plan 中的占位符 → 替换为空字符串（不要保留 `{{...}}` 字面值）

**HTML escaping 规则**：

- `page_title` / `key_message` / `on_slide_text.*` / `speaker_notes` / `caption` 等来自用户或 LLM 的文本字段，默认必须用 Python 标准库 `html.escape(value, quote=True)` 转义后再替换。
- 数组字段先逐项 escape，再由 `build_html.py` 拼成 `<li>`、`<p>` 或 snippet 约定的结构；不要把原始数组 `str(list)` 写进 HTML。
- `image_src` 只能来自本项目相对路径白名单（`images/slide-NN.png` / `.jpg` / `.jpeg` / `.webp` 或空字符串），不能接收用户任意 URL / JS URL。
- `image_block` 同样只能引用上述白名单路径；Mixed 不允许外链图片作为最终交付依赖。
- 只有 layout snippet 中已经写死的标签结构可进入最终 HTML；不支持把 Markdown 自动渲染进 slide body。
- 生成后 `validate_html.py` 必须检查最终 `index.html` 中没有残留 `{{...}}` 占位符。

**validate_slide_plan.py 语义检查（JSON Schema 之外）**：

JSON Schema 只负责字段形状；`validate_slide_plan.py` 还必须额外检查：

- `deck_meta.total_pages == len(pages)`
- `page_id` 唯一、连续、从 `P01` 开始，并与数组顺序一致
- 每个 `layout_type` 都存在对应 `assets/templates/layouts/<layout_type>.html.snippet`
- `deck_meta.style_name` 与 `source/style_lock.json.style_name` 一致（当 style lock 已存在）
- `image_requirement.text_in_image_risk == "high"` 时给 warning，提示优先 HTML 或减少可见文字

**禁止**：

- ❌ 在 build_html.py 里调用 LLM
- ❌ 在 build_html.py 里临时生成 CSS
- ❌ 在 build_html.py 里改 `style_lock.json` 的值
- ❌ 引入 npm / pip 额外依赖（标准库 + 已声明的项目依赖）

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
