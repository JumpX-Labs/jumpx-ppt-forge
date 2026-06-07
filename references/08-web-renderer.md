# 08 — Web Renderer

> Step 7B 落地文档。把 `slide_plan.json` + `style_lock.json` 渲染成单文件 HTML deck。
>
> **渲染方式**：由你（模型）**按设计 token 直接编写 `index.html`**，每页自由做版面设计——不是填模板。
> 这是唯一渲染路径（没有模板回退）；现代模型完全有能力写出专业水准的 HTML 幻灯片。

---

## 角色

> 切换到 **Web Renderer / 演示设计师**（Stripe / Linear / Apple Keynote 水准）。

职责：

- 按 `slide_plan.json` + `style_lock.json`，**直接写出 `<project>/index.html`**，每页按内容与角色做最合适的版面设计。
- 每页落地前重读 `source/style_lock.json`（铁律 6：抗上下文漂移）。
- 保证本地直接打开、横向翻页、键盘/触摸/ESC 索引可用。
- 输出后跑 `scripts/validate_html.py` 校验结构。

不做：

- 不发明 `style_lock.json` 之外的配色/字体（设计自由 ≠ 乱用色）。
- 不引任何外部资源（CDN / 外链字体 / 远程脚本）。

---

## 输入

- `source/slide_plan.json`（逐页内容：`page_title` / `key_message` / `on_slide_text` / `speaker_notes` / `visual_direction` / `layout_type` / `image_requirement`）
- `source/style_lock.json`（设计 token：配色 / 字体 / 字号锚点 / density / layout_bias / forbidden）

---

## 硬契约（必须严格遵守——否则演示/导出/翻页会坏）

1. **结构**：`<main id="deck" class="deck">` 内，**每页一个** `<section class="slide" data-page-id="P01" data-layout="...">`（P01、P02… 按序）；slide 数 = `deck_meta.total_pages`。
2. **布局**：`.deck{ position:fixed; inset:0; display:flex; flex-wrap:nowrap; width:(N*100)vw; height:100vh; transition:transform .4s ease }`；`.slide{ flex:0 0 100vw; width:100vw; height:100vh; overflow:hidden; position:relative }`。
3. **翻页**：内置 JS——`←/→/空格`、底部上一页/下一页按钮、ESC 缩略图索引、移动端滑动；切页统一用 `deck.style.transform = 'translateX(-' + i*100 + 'vw)'`。控件放 `<nav class="slide-controls">`，缩略图容器 `id="index" class="slide-index"`（这两个 class 是导出/演示约定，会被外部隐藏/驱动）。
4. **自包含**：所有 CSS/JS **内联**；不引外部资源（确定性靠渲染环境装好字体，不靠外链）。中文字体兜底用**跨平台全栈**，保证 deck 离开作者机器（Win / 旧 Mac / 安卓）仍有合理 CJK 字形：`"Noto Sans SC","Source Han Sans SC","PingFang SC","Microsoft YaHei","Hiragino Sans GB",sans-serif`。`style_lock.font_heading/font_body` 必须以这套兜底收尾。
5. **不溢出**：每页内容必须一屏放下（1280×720 基准），宁可精炼，遵守 `style_lock.density`。

---

## 设计要求（发挥能力，不要千篇一律）

- **每页按其内容与 `page_role_in_story` 自己决定版面**：封面有气场、对比页用左右/卡片、列点用网格或时间线、金句大留白、收尾有行动感。参考该页 `visual_direction` 构图。
- 强排版层级、充足留白、克制强调色；用卡片/分隔线/几何点缀/kicker 小标/页码。
- 用 `style_lock` 的配色与字体当基调，但**版式由你创造**；可用 CSS grid/flex、渐变、阴影、圆角、**内联 SVG 图标、CSS 画的简单示意图/图表**。
- `layout_type` 视为**强烈建议**而非死命令——内容更适合别的版面时可调整。严格遵守 `style_lock.forbidden`。

---

## 图片（Mixed / Image 路径）

- 可见图片只允许项目内 `images/slide-NN.{png,jpg,jpeg,webp}`；优先 `page.image_requirement.generated_image_path`，否则探测同名文件。
- `image_requirement.needed == true` 但文件不存在 → 渲染明确占位 `Image pending (slide-NN): <visual_direction>`，**禁止断裂 `<img>`**。
- 路径白名单：禁止 `http(s)://`、`data:`、`javascript:` 或任意外部/用户输入路径。
- 铁律 7 不变：Image 路径必须真出图，禁止用 HTML/SVG/Canvas 冒充 raster image。

---

## 验收标准

- `index.html` 存在、可本地直接打开、自包含（无外部资源）。
- `<main id="deck">` 存在；每个 `pages[]` 都有对应 `<section class="slide" data-page-id="...">`；页面数 = `deck_meta.total_pages`。
- 含键盘/触摸翻页 + ESC 索引脚本，切页走 `#deck` 的 `translateX`。
- 文本无明显溢出（遵守 density）；颜色/字体来自 `style_lock`。
- 跑 `scripts/validate_html.py` 通过。
