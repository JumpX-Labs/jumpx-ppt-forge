# 架构 · AI PPT Forge

> 这个 Skill 长什么样、各部分怎么协作。运行时 Agent 只需读 [`SKILL.md`](../SKILL.md)；本文给想理解/扩展它的人。

---

## 一句话模型

**输入（主题 + 资料 + 几个选择）→ 一条串行管线 → 自包含 HTML deck（或 AI 配图 deck）。**
管线里是多个"角色"接力，每个角色一份指令（`references/`）；关键处停下等人拍板；产物逐层落盘，可校验、可复现。

---

## 九步管线

```
1 Intake 意图澄清      → project_brief.md
2 Context Pack 资料吸收 → context_pack.md
3 Outline 大纲   ⛔Gate → outline.md            ← 停下：确认大纲
4 Slide Plan 逐页计划   → slide_plan.json        ← 每页：标题/要点/讲稿/视觉方向/版式
5 Narrative Review 审核 → review_report.md       ← 自动；最多返工 1 轮
6 Design Spec 设计定稿 ⛔Gate → style_lock.json  ← 停下：选风格（设计 token 锁定）
7 Render 渲染    ⛔Gate
    7A Image：每页 Prompt 落盘 → 调图片 backend → images/slide-NN.png
    7B HTML：模型按 style_lock 直接写 → index.html
8 Quality Check 质检    → qa_report.md
9 Delivery 交付         → runs/<项目>/（index.html + source/ + 可选 images/ prompts/）
```

**铁律**（`SKILL.md` 顶部）：严格串行、上一步输出是下一步输入；⛔BLOCKING 步必须停下等人；禁止预先生成后续产物；进入渲染前每页重读 `style_lock.json`（抗长上下文漂移）；Image 路径必须真出图、禁止用代码冒充。

---

## 角色与 references

每个角色一份指令文档，Agent 按需读取（渐进式披露）：

| # | 角色 | 职责 |
|---|------|------|
| 00 | 产品原则 | 全局价值观与红线 |
| 01 | Intake | 澄清目标/受众/输出形态/篇幅 |
| 02 | Context Pack | 把资料/主题吸收成结构化上下文 |
| 03 | Strategist | 叙事策略、页序、每页作用（**可改层** · 决定"讲什么、多深"）|
| 04 | Researcher | 资料不足时补事实/数据/例子 |
| 05 | Writer | 写逐页 `slide_plan.json`：标题/可见文本/讲稿（**可改层** · 决定"写多厚"）|
| 06 | Reviewer | 叙事审核，最多自动返工 1 轮 |
| 07 | Designer | 定风格、生成 `style_lock.json`（设计 token）|
| 08 | Web Renderer | **模型按设计 token 直接写 HTML**（唯一渲染路径，无模板）|
| 09 | Image Renderer | 每页 Prompt 落盘 + 调图片 backend |
| 10 | Style Guard | 渲染后核对是否守住 style_lock |
| 11 | Producer | 交付目录、命名、结果可见性 |
| 12 | Style Presets | 7 套风格语义档（**可改层**）|
| 13 | Regeneration | 局部重生某页的工作流 |
| 14 | Quality Checklist | 交付前质检项 |
| 15 | Export Contract | 三种交付目录树、文件命名 |

> **锁定层 vs 可改层**：管线骨架、门禁、schema、脚本、渲染契约是**锁定的引擎**（保证安全与可复现）；叙事(03)、写作(05)、风格(12)、背景知识是**可改层**——换这几样 = 换一个"会写某类 deck 的脑子"，引擎不变。

---

## 两条数据契约（产物的骨架）

- **`slide_plan.json`**（Step 4 产出，schema 强制）：每页 `page_title / key_message / on_slide_text{headline,body[],caption} / speaker_notes / visual_direction / layout_type / image_requirement`。这是"内容层"——渲染前可逐页审阅。
- **`style_lock.json`**（Step 6 产出）：配色 / 字体 / 字号锚点 / density / layout_bias / forbidden。这是"设计 token"——渲染时模型据此发挥，并逐页重读以防漂移。

schema 见 [`../schemas/`](../schemas/)。

---

## 渲染：模型直接写 HTML（唯一路径）

模型拿 `slide_plan.json` + `style_lock.json`（设计 token），**直接写出单文件 `index.html`**，每页按内容自由设计版面（`references/08-web-renderer.md`）。必须遵守**硬契约**让产物可演示/可导出：
- `<main id="deck">` 内每页一个 `<section class="slide">`（100vw×100vh，16:9）；
- `transform: translateX(-i*100vw)` 翻页 + 键盘/触摸/ESC 索引；
- 全内联、自包含、不引外部资源；不溢出；配色/字体来自 `style_lock`。

> **没有模板回退**：旧的"填模板片段"渲染（build_html + layout snippets）已彻底移除——版式质量不再被模板封顶。为什么这样更好，见 [`WHY-IT-WORKS.md`](WHY-IT-WORKS.md)。`layout_type` 现仅作"版面建议"，由模型据此构图。

---

## 输出形态（Output Mode）

| 模式 | 含义 |
|------|------|
| `html-only` | 纯网页（推荐上课）；跳过出图 |
| `image-first` | 每页真实出图（Image-first） |
| `mixed` | HTML 为主 + 局部配图 |
| `html-only-with-prompts` | 出 HTML，同时为指定页保留图片 Prompt |

图片路径需配置 backend（`.env`：OpenAI / Gemini / Nanobanana 等）；backend 不可用时自动切 HTML 并保留 Prompt（Prompt 是资产）。

---

## 脚本（纯 stdlib，不含 LLM）

`validate_slide_plan.py` / `validate_html.py` / `validate_context_lock.py` / `validate_images_manifest.py`（校验）· `generate_images.py` / `export_images_manifest.py` / `probe_image_backend.py`（出图）· `regenerate_slide.py`（标记局部重生）。HTML 由模型直接写，无渲染脚本。

---

## 可移植性

整个 skill 自包含、无私有运行时依赖——装进任何支持 Skill 的 Agent 即可运行；产物是自包含 HTML，脱离生成环境也能打开/演示/导出。这就是"在别家 Agent 也能复现同款效果"的基础。
