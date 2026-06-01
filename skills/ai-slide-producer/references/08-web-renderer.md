# 08 — Web Renderer

> Step 7B 落地文档。把 `slide_plan.json` + `style_lock.json` 渲染成单文件 HTML deck。
>
> **渲染哲学（重要变更）**：现代模型完全有能力写出专业水准的 HTML 幻灯片。本步骤的
> **主路径是「你（模型）直接编写 `index.html`，自由做版面设计」**——不是填死模板。
> 旧的 `scripts/build_html.py`（模板片段拼装）降级为**确定性回退**：当宿主不便由模型
> 长篇输出 HTML、需要纯脚本可复现、或批量/无人值守时使用。

---

## 角色

> 切换到 **Web Renderer / 演示设计师**。

职责：

- **主路径**：按 `slide_plan.json` + `style_lock.json`，**直接写出 `<project>/index.html`**，
  每页根据内容与角色做最合适的版面设计（达到 Stripe / Linear / Keynote 水准）。
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
- 参考：`assets/templates/layouts/*.html.snippet`（**作为版式灵感与回退**，非必须照搬）
- 回退脚本：`scripts/build_html.py` + `assets/styles/<style_name>.css`

---

## 主路径：模型直接写 HTML

### 硬契约（必须严格遵守——否则演示/导出/翻页会坏）

1. **结构**：`<main id="deck" class="deck">` 内，**每页一个** `<section class="slide" data-page-id="P01" data-layout="...">`（P01、P02… 按序）；slide 数 = `deck_meta.total_pages`。
2. **布局**：`.deck{ position:fixed; inset:0; display:flex; flex-wrap:nowrap; width:(N*100)vw; height:100vh; transition:transform .4s ease }`；`.slide{ flex:0 0 100vw; width:100vw; height:100vh; overflow:hidden; position:relative }`。
3. **翻页**：内置 JS——`←/→/空格`、底部上一页/下一页按钮、ESC 缩略图索引、移动端滑动；切页统一用 `deck.style.transform = 'translateX(-' + i*100 + 'vw)'`。控件放 `<nav class="slide-controls">`，缩略图容器 `id="index" class="slide-index"`（这两个 class 是导出/演示约定，会被外部隐藏/驱动）。
4. **自包含**：所有 CSS/JS **内联**；不引外部资源；中文字体兜底 `"Noto Sans SC","PingFang SC",sans-serif`。
5. **不溢出**：每页内容必须一屏放下（1280×720 基准），宁可精炼，遵守 `style_lock.density`。

### 设计要求（发挥能力，不要千篇一律）

- **每页按其内容与 `page_role_in_story` 自己决定版面**：封面有气场、对比页左右/卡片、列点用网格或时间线、金句大留白、收尾有行动感。参考该页 `visual_direction` 构图。
- 强排版层级、充足留白、克制使用强调色；用卡片/分隔线/几何点缀/kicker 小标/页码。
- 用 `style_lock` 的配色与字体当基调，但**版式由你创造**；可用 CSS grid/flex、渐变、阴影、圆角、**内联 SVG 图标、CSS 画的简单示意图/图表**。
- 严格遵守 `style_lock.forbidden`。`layout_type` 视为**强烈建议**而非死命令——内容更适合别的版面时可调整。

### 图片（Mixed / Image 路径）

- 可见图片只允许项目内 `images/slide-NN.{png,jpg,jpeg,webp}`；优先 `page.image_requirement.generated_image_path`，否则探测同名文件。
- `image_requirement.needed == true` 但文件不存在 → 渲染明确占位 `Image pending (slide-NN): <visual_direction>`，**禁止断裂 `<img>`**。
- 路径白名单：禁止 `http(s)://`、`data:`、`javascript:` 或任意外部/用户输入路径。
- 铁律 7 不变：Image 路径必须真出图，禁止用 HTML/SVG/Canvas 冒充 raster image。

---

## 回退路径：`scripts/build_html.py`（确定性模板）

当**不走模型直写**时（纯脚本可复现 / 批量 / 宿主限制），用模板片段拼装：

```bash
python3 scripts/build_html.py <project-dir>
python3 scripts/validate_html.py <project-dir>/index.html
```

支持 10 种 `layout_type`，每种对应 `assets/templates/layouts/<layout_type>.html.snippet`，CSS 来自 `assets/styles/<style_name>.css`。占位符映射与 body 约定见本文件末「附：模板回退映射」。回退路径质量受模板封顶，仅保底用。

---

## 验收标准（两条路径通用）

- `index.html` 存在、可本地直接打开。
- 无残留 `{{placeholder}}`。
- `<main id="deck">` 存在；每个 `pages[]` 都有对应 `<section class="slide" data-page-id="...">`；页面数 = `deck_meta.total_pages`。
- 含键盘/触摸翻页 + ESC 索引脚本，切页走 `#deck` 的 `translateX`。
- 自包含、无外部资源。
- 文本无明显溢出（遵守 density）。
- 跑 `scripts/validate_html.py` 通过。

---

## 附：模板回退映射（仅 build_html.py 路径用）

| Layout | Snippet | 主要占位符 | body 约定 |
|--------|---------|------------|-----------|
| `cover` | `cover.html.snippet` | `page_title`, `key_message`, `deck_title` | 通常不用 `body` |
| `section-divider` | `section-divider.html.snippet` | `page_number`, `page_title`, `key_message` | 通常不用 `body` |
| `big-idea` | `big-idea.html.snippet` | `key_message`, `sub_headline` | 通常不用 `body` |
| `two-column` | `two-column.html.snippet` | `headline`, `two_column_lead`, `body_items` | `body[0]` 进左栏说明；`body[1..]` 进右栏列表 |
| `quote` | `quote.html.snippet` | `key_message`, `caption` | 通常不用 `body` |
| `framework` | `framework.html.snippet` | `tiles` | 每条 `标题:正文`；最多 6 条 |
| `timeline` | `timeline.html.snippet` | `steps` | 每条 `阶段:说明`；最多 6 条 |
| `comparison` | `comparison.html.snippet` | `comparison_panels` | 每条 `标题:正文`；最多 4 条 |
| `image-text` | `image-text.html.snippet` | `image_block`, `key_message`, `body_items` | `body` 全部进右侧列表 |
| `closing` | `closing.html.snippet` | `tiles` | 每条 `行动:说明`；最多 6 条 |

回退路径下：文本必须 HTML escape；禁止在 `build_html.py` 里生成 CSS（CSS 来自 `assets/styles/`）；禁止修改 `style_lock.json`。
