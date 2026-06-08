# Examples

本目录存放 **AI PPT Forge** 的固定回归样例。所有路径均相对于 `skills/ai-slide-producer/`。

---

## 样例一览

| 目录 | 页数 | 用途 |
|------|------|------|
| [`teaching-clean-demo/`](teaching-clean-demo/) | 4 | **叙事冒烟**：工作流介绍，4 种 layout |
| [`teaching-clean-layout-gallery/`](teaching-clean-layout-gallery/) | 10 | **全 layout 回归**：10 种 `layout_type` 各一页 |
| [`editorial-magazine-demo/`](editorial-magazine-demo/) | 8 | **高视觉 HTML**：`editorial-magazine` preset + 4 项 comparison |
| [`editorial-magazine-mixed-demo/`](editorial-magazine-mixed-demo/) | 8 | **Mixed**：HTML 嵌入本地 `images/slide-NN.png` |
| [`editorial-magazine-image-first-demo/`](editorial-magazine-image-first-demo/) | 5 | **Image-first**：prompts + manifest + 占位/真图 |
| [`swiss-system-demo/`](swiss-system-demo/) | 4 | **Swiss preset**：网格、高密度结构 |
| [`spacex-ipo/`](spacex-ipo/) | 6 | **观点型 editorial（README Case 01）**：`editorial-magazine` 观点弧 + 数字/词锚 + 深色金句页，新版 craft rules 实战，全套九步中间产物 |

**区别**：demo 证明「管线能跑」；gallery 证明「十种 layout 片段都能渲染」。改 `layouts/`、`styles/` 或 `build_html.py` 后优先跑 gallery。

Layout Gallery 任务书（维护者）：[`docs/teaching-clean-layout-gallery-prd_v1.md`](../../docs/teaching-clean-layout-gallery-prd_v1.md)

---

## 回归命令

在 `skills/ai-slide-producer/` 下执行。

### Demo（4 页）

```bash
python3 scripts/validate_slide_plan.py \
  assets/examples/teaching-clean-demo/source/slide_plan.json
python3 scripts/validate_context_lock.py \
  assets/examples/teaching-clean-demo/source/style_lock.json
python3 scripts/build_html.py assets/examples/teaching-clean-demo
python3 scripts/validate_html.py \
  assets/examples/teaching-clean-demo/index.html
```

### Layout Gallery（10 页）

```bash
python3 scripts/validate_slide_plan.py \
  assets/examples/teaching-clean-layout-gallery/source/slide_plan.json
python3 scripts/validate_context_lock.py \
  assets/examples/teaching-clean-layout-gallery/source/style_lock.json
python3 scripts/build_html.py assets/examples/teaching-clean-layout-gallery
python3 scripts/validate_html.py \
  assets/examples/teaching-clean-layout-gallery/index.html
```

### Editorial Magazine（8 页，高视觉 HTML）

```bash
python3 scripts/validate_slide_plan.py \
  assets/examples/editorial-magazine-demo/source/slide_plan.json
python3 scripts/validate_context_lock.py \
  assets/examples/editorial-magazine-demo/source/style_lock.json
python3 scripts/build_html.py assets/examples/editorial-magazine-demo
python3 scripts/validate_html.py \
  assets/examples/editorial-magazine-demo/index.html
```

期望：视觉明显强于 `teaching-clean`；P06 comparison 渲染 4 个 panel。

### Editorial Magazine Mixed（8 页）

```bash
python3 scripts/validate_slide_plan.py \
  assets/examples/editorial-magazine-mixed-demo/source/slide_plan.json
python3 scripts/validate_context_lock.py \
  assets/examples/editorial-magazine-mixed-demo/source/style_lock.json
python3 scripts/build_html.py assets/examples/editorial-magazine-mixed-demo
python3 scripts/validate_html.py \
  assets/examples/editorial-magazine-mixed-demo/index.html
```

期望：P04 / P07 显示 `<img src="images/slide-04.png">` 等本地图。

### Editorial Magazine Image-first（5 页）

```bash
python3 scripts/validate_slide_plan.py \
  assets/examples/editorial-magazine-image-first-demo/source/slide_plan.json
python3 scripts/validate_context_lock.py \
  assets/examples/editorial-magazine-image-first-demo/source/style_lock.json
python3 scripts/validate_images_manifest.py \
  assets/examples/editorial-magazine-image-first-demo
python3 scripts/build_html.py assets/examples/editorial-magazine-image-first-demo
python3 scripts/validate_html.py \
  assets/examples/editorial-magazine-image-first-demo/index.html
```

期望：`prompts/` 与 `images_manifest.json` 对齐；真出图冒烟建议 `--only P01`。

### Swiss System（4 页）

```bash
python3 scripts/validate_slide_plan.py \
  assets/examples/swiss-system-demo/source/slide_plan.json
python3 scripts/validate_context_lock.py \
  assets/examples/swiss-system-demo/source/style_lock.json
python3 scripts/build_html.py assets/examples/swiss-system-demo
python3 scripts/validate_html.py \
  assets/examples/swiss-system-demo/index.html
```

### 脚本语法检查（可选）

```bash
python3 -m py_compile scripts/*.py
```

---

## 导出图片 Prompt（不调用 API）

```bash
python3 scripts/export_images_manifest.py \
  assets/examples/teaching-clean-demo --include-all --backend none
python3 scripts/validate_images_manifest.py \
  assets/examples/teaching-clean-demo
```

期望：`prompts/`、`images_manifest.json` 存在；状态 `pending`；不创建 PNG。

---

## 出图冒烟（需 `.env`）

```bash
python3 scripts/generate_images.py \
  assets/examples/teaching-clean-demo --backend openai --dry-run
python3 scripts/generate_images.py \
  assets/examples/teaching-clean-demo --backend openai --only P01
```

无 Key 时保持 `pending`，不生成占位图。

---

## 局部重生（建议在副本上跑）

```bash
cp -R assets/examples/teaching-clean-demo /tmp/asp-demo-regenerate
python3 scripts/regenerate_slide.py /tmp/asp-demo-regenerate P03
python3 scripts/validate_html.py /tmp/asp-demo-regenerate/index.html
```

---

## 目录约定

```text
<example-name>/
├── index.html              # build_html 生成（建议提交）
└── source/
    ├── slide_plan.json
    └── style_lock.json
```

`html-only` 回归不需要 `prompts/`、`images/`。

---

## 手工检查

1. 双击 `index.html`
2. ← / → 翻页，ESC 缩略图
3. 无残留 `{{placeholder}}`，控制台无 JS 报错
