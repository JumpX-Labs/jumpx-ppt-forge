# 12 — 视觉风格（Style Presets）

> Step 2 / Step 6 / Step 7 共用。说明 7 套内置风格：何时选用、网页版怎么渲染、出图 Prompt 怎么写。

---

## 使用位置

| 阶段 | 使用方式 |
|------|----------|
| Step 2 Context Pack | 根据场景、受众、输出形态选择 `style_name` |
| Step 4 Writer | 根据 preset 控制页面密度、layout 倾向、图片页比例 |
| Step 6 Designer | 从 `assets/style-presets/<style_name>.json` 写入 `style_lock.json` |
| Step 7B Web Renderer | `build_html.py` 按 `style_lock.style_name` 加载 `assets/styles/<style_name>.css` |
| Step 7A Image Renderer | 从 preset 的 `image_style_description` 与 `negative_constraints` 生成每页 prompt |
| Step 8 Style Guard | 对照 preset 检查风格漂移 |

---

## 选择总原则

- 用户显式指定风格时优先采纳，但必须映射到 7 套之一。
- 用户只说“高级一点 / 更有设计感 / 对外展示”时，默认 `editorial-magazine`。
- 教学、训练营、课程正文默认 `teaching-clean`；对外 demo 或开场页可用 `editorial-magazine`。
- 信息密集、咨询、方法论、技术路线默认 `swiss-system`。
- 技术架构、系统方案、产品蓝图默认 `blueprint`。
- 社群传播、轻松分享、手写感默认 `sketch-notes`。
- 企业汇报、管理层同步默认 `corporate`。
- 个人 IP、短视频脚本、社媒轮播默认 `creator-social`。

---

## 7 套风格一览

| Preset（id） | 展示名 | 何时选 |
|--------------|--------|--------|
| `teaching-clean` | Teaching Clean | 教学课件、概念讲解、训练营正文 |
| `editorial-magazine` | Editorial Magazine | 对外展示、演讲开场、产品发布、强叙事 |
| `swiss-system` | Swiss System | 咨询汇报、技术路线、信息密集、理性表达 |
| `blueprint` | Blueprint | 技术架构、系统设计、路线图、工程方案 |
| `sketch-notes` | Sketch Notes | 轻松分享、社群传播、教学互动 |
| `corporate` | Corporate | 商务汇报、管理层材料、稳重方案 |
| `creator-social` | Creator Social | 个人 IP、短视频脚本、社媒轮播 |

每套均配有 `assets/styles/<id>.css`（网页）与 `assets/style-presets/<id>.json`（出图描述）。

---

## HTML / Image 分工

### HTML

HTML preset 是真实 CSS，必须保存在：

```text
assets/styles/<style_name>.css
```

Web Renderer 的契约：

- 不手写最终 `index.html`。
- 由 `scripts/build_html.py <project>` 读取 `source/style_lock.json`。
- 根据 `style_lock.style_name` 加载对应 CSS。
- CSS 适配现有 10 种 layout 片段。
- CSS 不应覆盖 `build_html.py` 注入的核心变量：`--asp-bg`、`--asp-ink`、`--asp-accent`、`--asp-font-heading`、`--asp-font-body`。需要扩展时使用新变量。

### Image

Image preset 是给图像模型的视觉描述，必须保存在：

```text
assets/style-presets/<style_name>.json
```

Image Renderer 使用：

- `image_style_description`
- `texture`
- `mood`
- `typography`
- `density`
- `color_palette`
- `layout_bias`
- `negative_constraints`

可见文字仍来自 `slide_plan.json.pages[].on_slide_text`，不能让图片模型自由改写。

---

## Preset 细则

### teaching-clean

定位：清楚、克制、教学友好。

适合：

- 训练营主课件。
- 概念拆解。
- 长正文较多、需要稳定中文显示的 HTML slides。

避免：

- 对外展示的首屏 demo。
- 需要强情绪、强品牌感的发布场景。

HTML 执行：

- 白底浅灰、轻卡片、8px 半径。
- 保持工程回归基线。

Image 执行：

- clean educational diagram。
- simple geometric illustration。
- soft editorial screenshot。

### editorial-magazine

定位：电子杂志、强标题、强对比、可展示。

适合：

- 对外展示默认 preset。
- 训练营开场页或成果页。
- 产品发布、观点型演讲、公开分享。
- 用户说“更好看 / 更有设计感 / 杂志感”。

避免：

- 高密度表格。
- 需要极端严肃的企业财务材料。
- 需要大量中文正文的每一页都图片化。

HTML 执行：

- 暖纸底 + 墨色大标题。
- 封面、章节、金句页允许深色整页。
- 卡片更像 editorial module，不做灰卡片模板站。
- 使用同一套现有 snippet，通过 CSS 提升视觉档。

Image 执行：

- magazine cover composition。
- bold editorial typography。
- paper texture, ink contrast, restrained color blocks。
- 禁止廉价渐变、卡通商务插画、过满贴纸感。

### swiss-system

定位：瑞士国际主义、网格、理性、高反差。

适合：

- 咨询汇报。
- 技术路线。
- 方法论框架。
- 信息密集但需要看起来高级的 deck。

避免：

- 手绘感、故事感、情绪化品牌页。
- 多色彩、多装饰、照片拼贴。

HTML 执行：

- 高级灰白底 + 单一高饱和 accent。
- 明确网格、直角、细线、编号系统。
- 不使用渐变、阴影、圆角装饰。

Image 执行：

- Swiss poster grid。
- Helvetica-like typography。
- black / off-white / single accent color。
- 直线、编号、几何块；禁止渐变和多 accent 混搭。

### blueprint

定位：技术蓝图、架构、工程方案。

适合：

- 系统架构。
- 产品路线图。
- 技术方案。
- 工程培训。

HTML 执行：

- 浅底技术纸、细网格、工程蓝。
- 卡片为直角线框，不用照片和装饰渐变。
- 适合 `framework` / `timeline` / `comparison` 的结构表达。

Image 执行：

- precise technical blueprint。
- engineering grid, schematic, dimension lines。

### sketch-notes

定位：轻松、手绘、传播友好。

适合：

- 轻课程。
- 社群分享。
- 工作坊。
- 方法卡片。

HTML 执行：

- 暖纸底、虚线边框、手写感字体。
- 内容模块允许轻微旋转和手绘符号。
- 保持低到中低密度，避免把手写风做成杂乱贴纸。

Image 执行：

- hand-drawn sketch notes。
- marker line, simple icons, playful but readable。

### corporate

定位：商务、稳重、克制。

适合：

- 企业汇报。
- 方案提案。
- 管理层同步。
- 内部复盘。

HTML 执行：

- 白底、海军蓝结构、金色强调。
- 控制阴影和圆角，偏 executive / proposal。
- 适合稳定输出 `two-column`、`framework`、`closing`。

Image 执行：

- polished corporate presentation visual。
- restrained palette, professional diagrams。

### creator-social

定位：个人 IP、社媒、轻发布。

适合：

- 社媒轮播。
- 短视频脚本配套。
- 个人作品集。
- 自解释阅读材料。

HTML 执行：

- 浅灰背景、白色产品卡片、蓝/绿强调。
- 标题大、节奏快，适合自解释阅读与社媒轮播。
- 保持 screen-first 可读性，不做复杂装饰背景。

Image 执行：

- clean creator carousel。
- high contrast title cards, friendly product screenshots。

---

## Designer 写入 `style_lock.json` 的规则

从 `assets/style-presets/<style_name>.json` 复制：

- `style_name`
- `color_palette.primary_color`
- `color_palette.accent_color`
- `color_palette.background_color`
- `color_palette.text_primary_color`
- `color_palette.text_secondary_color`
- `color_palette.border_color`
- `font_heading`
- `font_body`
- `image_style_description` -> `image_style`
- `density`
- `layout_bias`
- `negative_constraints` 中的硬规则可追加到 `forbidden`

`style_lock.json` 是 Gate 4 后的执行锁。后续 Web / Image 每页渲染前必须重读。

---

## Agent 自检（选用风格后）

- `style_name` 必须是上表 7 个 id 之一。
- 对应 `assets/styles/<style_name>.css` 与 `assets/style-presets/<style_name>.json` 存在。
- Step 6 的 `style_lock.json` 与 Context Pack 中的 `style_name` 一致。
